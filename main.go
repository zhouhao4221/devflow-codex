package main

import (
	"bufio"
	"bytes"
	"embed"
	"encoding/json"
	"flag"
	"fmt"
	"io/fs"
	"os"
	"os/exec"
	"path/filepath"
	"sort"
	"strings"
)

//go:embed plugins
var skillsFS embed.FS

type skillLayout int

const (
	layoutFlat        skillLayout = iota
	layoutHierarchical
)

type toolConfig struct {
	name            string
	projectSkillsDir string
	globalSkillsDir  string
	layout          skillLayout
}

var tools = map[string]toolConfig{
	"opencode":  {name: "opencode", projectSkillsDir: ".agents/skills", globalSkillsDir: ".config/opencode/skills", layout: layoutFlat},
	"codex":     {name: "codex", projectSkillsDir: ".agents/skills", globalSkillsDir: ".config/codex/skills", layout: layoutFlat},
	"claude":    {name: "claude", projectSkillsDir: "plugins", globalSkillsDir: "plugins", layout: layoutHierarchical},
	"cursor":    {name: "cursor", projectSkillsDir: ".agents/skills", globalSkillsDir: ".cursor/skills", layout: layoutFlat},
	"copilot":   {name: "copilot", projectSkillsDir: ".agents/skills", globalSkillsDir: ".github/copilot/skills", layout: layoutFlat},
	"codebuddy": {name: "codebuddy", projectSkillsDir: ".agents/skills", globalSkillsDir: ".config/codebuddy/skills", layout: layoutFlat},
	"windsurf":  {name: "windsurf", projectSkillsDir: ".agents/skills", globalSkillsDir: ".config/windsurf/skills", layout: layoutFlat},
}

type skillInfo struct {
	Plugin  string
	Name    string
	Desc    string
	RawPath string
	Content []byte
}

func main() {
	if len(os.Args) < 2 {
		printUsage()
		os.Exit(1)
	}

	cmd := os.Args[1]
	switch cmd {
	case "install":
		runInstall(os.Args[2:])
	case "list":
		runList(os.Args[2:])
	case "uninstall":
		runUninstall(os.Args[2:])
	case "add":
		runAdd(os.Args[2:])
	case "help", "-h", "--help":
		printUsage()
	default:
		fmt.Fprintf(os.Stderr, "未知命令: %s\n\n", cmd)
		printUsage()
		os.Exit(1)
	}
}

func printUsage() {
	fmt.Print(`devflow-skills — AI 技能一键安装/管理工具

用法:
  devflow-skills install   --tool <TOOL> [--skill <NAME>...] [--all] [--dir <PATH>] [--global] [--symlink]
  devflow-skills list      [--plugin <NAME>] [--format text|json]
  devflow-skills uninstall --tool <TOOL> [--skill <NAME>...] [--all] [--dir <PATH>] [--global]
  devflow-skills add       <owner/repo> [--tool <TOOL>] [--skill <NAME>...] [--all] [--list] [--dir <PATH>] [--global] [--symlink]

命令:
  install     安装技能到目标 AI 工具目录
  list        列出所有可用技能
  uninstall   从目标 AI 工具目录卸载技能
  add         从 GitHub 仓库克隆并安装技能

支持的 --tool 值: opencode, claude, codex, cursor, copilot, codebuddy, windsurf

示例:
  npx devflow-skills install --tool opencode --all
  npx devflow-skills install --tool cursor --skill req-dev
  npx devflow-skills install --tool opencode --all -g
  npx devflow-skills install --tool cursor --all --symlink
  npx devflow-skills list --plugin req
  npx devflow-skills uninstall --tool opencode --all
  npx devflow-skills add zhouhao4221/devflow-skills --tool copilot --all
  npx devflow-skills add zhouhao4221/devflow-skills --list
`)
}

func validateTool(tool string) (toolConfig, error) {
	cfg, ok := tools[tool]
	if !ok {
		var names []string
		for n := range tools {
			names = append(names, n)
		}
		sort.Strings(names)
		return toolConfig{}, fmt.Errorf("不支持的 --tool 值: %s (支持: %s)", tool, strings.Join(names, ", "))
	}
	return cfg, nil
}

func targetBase(cfg toolConfig, dir string, global bool) string {
	if global {
		home, _ := os.UserHomeDir()
		return filepath.Join(home, cfg.globalSkillsDir)
	}
	return filepath.Join(dir, cfg.projectSkillsDir)
}

func targetPath(cfg toolConfig, dir string, global bool, plugin, name string) string {
	base := targetBase(cfg, dir, global)
	if cfg.layout == layoutHierarchical {
		return filepath.Join(base, plugin, "skills", name)
	}
	return filepath.Join(base, plugin+"-"+name)
}

func canonicalBase(dir string, global bool) string {
	if global {
		home, _ := os.UserHomeDir()
		return filepath.Join(home, ".agents", "skills")
	}
	return filepath.Join(dir, ".agents", "skills")
}

func canonicalPath(dir string, global bool, plugin, name string) string {
	return filepath.Join(canonicalBase(dir, global), plugin+"-"+name)
}

func runInstall(args []string) {
	fs := flag.NewFlagSet("install", flag.ExitOnError)
	tool := fs.String("tool", "", "目标 AI 工具: opencode / claude / codex / cursor / copilot / codebuddy / windsurf")
	allFlag := fs.Bool("all", false, "安装所有技能")
	dir := fs.String("dir", ".", "目标项目根目录")
	global := fs.Bool("global", false, "安装到全局目录")
	symlink := fs.Bool("symlink", false, "使用符号链接安装到规范目录")
	var skills skillsFlag
	fs.Var(&skills, "skill", "要安装的技能名")
	fs.Bool("g", false, "--global 的短选项")
	fs.Parse(args)

	if *tool == "" {
		fmt.Fprintln(os.Stderr, "错误: --tool 是必需参数")
		os.Exit(1)
	}
	cfg, err := validateTool(*tool)
	if err != nil {
		fmt.Fprintln(os.Stderr, "错误:", err)
		os.Exit(1)
	}
	if !*allFlag && len(skills) == 0 {
		fmt.Fprintln(os.Stderr, "错误: 请指定 --skill 或 --all")
		os.Exit(1)
	}
	if *allFlag && len(skills) > 0 {
		fmt.Fprintln(os.Stderr, "错误: --skill 与 --all 不能同时使用")
		os.Exit(1)
	}

	allSkills, err := loadAllSkills()
	if err != nil {
		fmt.Fprintf(os.Stderr, "加载技能失败: %v\n", err)
		os.Exit(1)
	}

	var selected []skillInfo
	if *allFlag {
		selected = allSkills
	} else {
		for _, name := range skills {
			matched := resolveSkill(name, allSkills)
			if len(matched) == 0 {
				fmt.Fprintf(os.Stderr, "错误: 未找到技能 '%s'\n", name)
				fmt.Fprintf(os.Stderr, "使用 'devflow-skills list' 查看所有可用技能\n")
				os.Exit(1)
			}
			if len(matched) > 1 {
				fmt.Fprintf(os.Stderr, "错误: 技能名 '%s' 匹配到多个技能:\n", name)
				for _, s := range matched {
					fmt.Fprintf(os.Stderr, "  %s-%s: %s\n", s.Plugin, s.Name, s.Desc)
				}
				fmt.Fprintf(os.Stderr, "请使用完整的扁平名 (如 req-dev) 来区分\n")
				os.Exit(1)
			}
			selected = append(selected, matched[0])
		}
	}

	installed := 0
	for _, s := range selected {
		content, err := skillsFS.ReadFile(s.RawPath)
		if err != nil {
			fmt.Fprintf(os.Stderr, "读取技能 %s-%s 失败: %v\n", s.Plugin, s.Name, err)
			continue
		}
		if err := installSkill(cfg, *dir, *global, *symlink, s.Plugin, s.Name, content); err != nil {
			fmt.Fprintf(os.Stderr, "安装 %s-%s 失败: %v\n", s.Plugin, s.Name, err)
			continue
		}
		installed++
		if !*allFlag || installed <= 10 {
			fmt.Printf("  %s-%s (%s)\n", s.Plugin, s.Name, s.Desc)
		} else if installed == 11 {
			fmt.Println("  ...")
		}
	}

	fmt.Printf("\n已安装 %d 个技能到 %s/\n", installed, targetBase(cfg, *dir, *global))
	fmt.Println("下一步: 重启 AI 工具或刷新技能列表即可使用。")
}

func runList(args []string) {
	fs := flag.NewFlagSet("list", flag.ExitOnError)
	plugin := fs.String("plugin", "", "按插件过滤: req / api / pm / diag / uat")
	format := fs.String("format", "text", "输出格式: text / json")

	fs.Parse(args)

	allSkills, err := loadAllSkills()
	if err != nil {
		fmt.Fprintf(os.Stderr, "加载技能失败: %v\n", err)
		os.Exit(1)
	}

	type pluginGroup struct {
		Plugin string
		Skills []skillInfo
	}

	groups := make(map[string]*pluginGroup)
	for _, s := range allSkills {
		if *plugin != "" && s.Plugin != *plugin {
			continue
		}
		if g, ok := groups[s.Plugin]; ok {
			g.Skills = append(g.Skills, s)
		} else {
			groups[s.Plugin] = &pluginGroup{Plugin: s.Plugin, Skills: []skillInfo{s}}
		}
	}

	pluginOrder := []string{"req", "api", "pm", "diag", "uat"}
	if *plugin != "" {
		pluginOrder = []string{*plugin}
	}

	if *format == "json" {
		output := make(map[string][]map[string]string)
		for _, p := range pluginOrder {
			g, ok := groups[p]
			if !ok {
				continue
			}
			skills := make([]map[string]string, 0, len(g.Skills))
			for _, s := range g.Skills {
				skills = append(skills, map[string]string{
					"name":        s.Name,
					"flatName":    s.Plugin + "-" + s.Name,
					"description": s.Desc,
				})
			}
			output[p] = skills
		}
		enc := json.NewEncoder(os.Stdout)
		enc.SetIndent("", "  ")
		enc.Encode(output)
		return
	}

	for _, p := range pluginOrder {
		g, ok := groups[p]
		if !ok {
			continue
		}
		fmt.Printf("%s 插件 (%d 个技能):\n", pluginLabel(p), len(g.Skills))
		for _, s := range g.Skills {
			fmt.Printf("  %-22s %s\n", s.Plugin+"-"+s.Name, s.Desc)
		}
		fmt.Println()
	}
}

func runUninstall(args []string) {
	fs := flag.NewFlagSet("uninstall", flag.ExitOnError)
	tool := fs.String("tool", "", "目标 AI 工具")
	allFlag := fs.Bool("all", false, "卸载所有技能")
	dir := fs.String("dir", ".", "目标项目根目录")
	global := fs.Bool("global", false, "卸载全局安装的技能")
	var skills skillsFlag
	fs.Var(&skills, "skill", "要卸载的技能名")
	fs.Bool("g", false, "--global 的短选项")
	fs.Parse(args)

	if *tool == "" {
		fmt.Fprintln(os.Stderr, "错误: --tool 是必需参数")
		os.Exit(1)
	}
	cfg, err := validateTool(*tool)
	if err != nil {
		fmt.Fprintln(os.Stderr, "错误:", err)
		os.Exit(1)
	}
	if !*allFlag && len(skills) == 0 {
		fmt.Fprintln(os.Stderr, "错误: 请指定 --skill 或 --all")
		os.Exit(1)
	}
	if *allFlag && len(skills) > 0 {
		fmt.Fprintln(os.Stderr, "错误: --skill 与 --all 不能同时使用")
		os.Exit(1)
	}

	if *allFlag {
		base := targetBase(cfg, *dir, *global)
		absBase, err := filepath.Abs(base)
		if err != nil {
			fmt.Fprintf(os.Stderr, "获取路径失败: %v\n", err)
			os.Exit(1)
		}
		if _, err := os.Stat(absBase); os.IsNotExist(err) {
			fmt.Printf("技能目录不存在: %s\n", absBase)
			fmt.Println("无需卸载。")
			return
		}
		if err := os.RemoveAll(absBase); err != nil {
			fmt.Fprintf(os.Stderr, "删除目录失败: %v\n", err)
			os.Exit(1)
		}
		fmt.Printf("已卸载所有技能，删除目录: %s\n", absBase)

		canonical := canonicalBase(*dir, *global)
		if _, err := os.Stat(canonical); err == nil {
			fmt.Fprintf(os.Stderr, "注意: 规范目录 %s 仍存在，如使用过 --symlink 模式可能需要手动清理\n", canonical)
		}
		return
	}

	removed := 0
	for _, name := range skills {
		parts := strings.SplitN(name, "-", 2)
		var plugin, skillName string
		if len(parts) == 2 {
			plugin = parts[0]
			skillName = parts[1]
		} else {
			allSkills, err := loadAllSkills()
			if err != nil {
				fmt.Fprintf(os.Stderr, "加载技能失败: %v\n", err)
				os.Exit(1)
			}
			matched := resolveSkill(name, allSkills)
			if len(matched) != 1 {
				fmt.Fprintf(os.Stderr, "错误: 无法解析技能名 '%s'，请使用扁平名如 req-dev\n", name)
				os.Exit(1)
			}
			plugin = matched[0].Plugin
			skillName = matched[0].Name
		}

		target := targetPath(cfg, *dir, *global, plugin, skillName)
		if _, err := os.Stat(target); os.IsNotExist(err) {
			fmt.Printf("未安装: %s-%s\n", plugin, skillName)
			continue
		}
		if err := os.RemoveAll(target); err != nil {
			fmt.Fprintf(os.Stderr, "卸载 %s-%s 失败: %v\n", plugin, skillName, err)
			continue
		}
		fmt.Printf("已卸载: %s-%s\n", plugin, skillName)
		removed++
	}

	if removed == 0 {
		fmt.Println("没有需要卸载的技能。")
	} else {
		fmt.Printf("\n已卸载 %d 个技能。\n", removed)
	}
}

func runAdd(args []string) {
	repo := ""
	var flagArgs []string
	for _, a := range args {
		if !strings.HasPrefix(a, "-") && !strings.Contains(a, "=") && repo == "" {
			repo = a
		} else {
			flagArgs = append(flagArgs, a)
		}
	}

	fs := flag.NewFlagSet("add", flag.ExitOnError)
	tool := fs.String("tool", "", "目标 AI 工具 (省略时使用 --list)")
	allFlag := fs.Bool("all", false, "安装所有技能")
	listOnly := fs.Bool("list", false, "仅列出仓库中可用技能，不安装")
	dir := fs.String("dir", ".", "目标项目根目录")
	global := fs.Bool("global", false, "安装到全局目录")
	symlink := fs.Bool("symlink", false, "使用符号链接安装到规范目录")
	var skills skillsFlag
	fs.Var(&skills, "skill", "要安装的技能名")
	fs.Bool("g", false, "--global 的短选项")
	fs.Parse(flagArgs)

	if repo == "" {
		fmt.Fprintln(os.Stderr, "错误: 请指定仓库 (格式: owner/repo)")
		fmt.Fprintln(os.Stderr, "示例: devflow-skills add zhouhao4221/devflow-skills --list")
		os.Exit(1)
	}

	if !strings.Contains(repo, "/") {
		fmt.Fprintln(os.Stderr, "错误: 仓库格式无效，请使用 owner/repo 格式")
		os.Exit(1)
	}

	if !*listOnly && *tool == "" {
		fmt.Fprintln(os.Stderr, "错误: 安装模式下需要 --tool 参数")
		fmt.Fprintln(os.Stderr, "使用 --list 可以仅列出技能而不安装: devflow-skills add "+repo+" --list")
		os.Exit(1)
	}

	var cfg toolConfig
	if *tool != "" {
		var err error
		cfg, err = validateTool(*tool)
		if err != nil {
			fmt.Fprintln(os.Stderr, "错误:", err)
			os.Exit(1)
		}
	}

	if !*listOnly && !*allFlag && len(skills) == 0 {
		fmt.Fprintln(os.Stderr, "错误: 请指定 --skill 或 --all")
		os.Exit(1)
	}
	if *allFlag && len(skills) > 0 {
		fmt.Fprintln(os.Stderr, "错误: --skill 与 --all 不能同时使用")
		os.Exit(1)
	}

	repoSkills, err := fetchRepoSkills(repo)
	if err != nil {
		fmt.Fprintf(os.Stderr, "从仓库获取技能失败: %v\n", err)
		os.Exit(1)
	}

	var selected []skillInfo
	selected = repoSkills

	if *listOnly {
		displayRepoSkills(repo, repoSkills)
		return
	}

	if !*allFlag && len(skills) > 0 {
		selected = nil
		for _, name := range skills {
			matched := resolveSkill(name, repoSkills)
			if len(matched) == 0 {
				fmt.Fprintf(os.Stderr, "错误: 仓库中未找到技能 '%s'\n", name)
				fmt.Fprintf(os.Stderr, "使用 --list 查看仓库中的可用技能\n")
				os.Exit(1)
			}
			if len(matched) > 1 {
				fmt.Fprintf(os.Stderr, "错误: 技能名 '%s' 匹配到多个技能:\n", name)
				for _, s := range matched {
					fmt.Fprintf(os.Stderr, "  %s-%s: %s\n", s.Plugin, s.Name, s.Desc)
				}
				os.Exit(1)
			}
			selected = append(selected, matched[0])
		}
	}

	installed := 0
	for _, s := range selected {
		if err := installSkill(cfg, *dir, *global, *symlink, s.Plugin, s.Name, s.Content); err != nil {
			fmt.Fprintf(os.Stderr, "安装 %s-%s 失败: %v\n", s.Plugin, s.Name, err)
			continue
		}
		installed++
		if !*allFlag || installed <= 10 {
			fmt.Printf("  %s-%s (%s)\n", s.Plugin, s.Name, s.Desc)
		} else if installed == 11 {
			fmt.Println("  ...")
		}
	}

	fmt.Printf("\n已从 %s 安装 %d 个技能到 %s/\n", repo, installed, targetBase(cfg, *dir, *global))
	fmt.Println("下一步: 重启 AI 工具或刷新技能列表即可使用。")
}

func fetchRepoSkills(repo string) ([]skillInfo, error) {
	tmpDir, err := os.MkdirTemp("", "devflow-skills-*")
	if err != nil {
		return nil, fmt.Errorf("创建临时目录失败: %w", err)
	}
	defer os.RemoveAll(tmpDir)

	repoURL := fmt.Sprintf("https://github.com/%s.git", repo)
	cmd := exec.Command("git", "clone", "--depth", "1", repoURL, tmpDir)
	cmd.Stderr = os.Stderr
	fmt.Fprintf(os.Stderr, "正在克隆 %s...\n", repoURL)
	if err := cmd.Run(); err != nil {
		return nil, fmt.Errorf("git clone 失败: %w", err)
	}

	var skills []skillInfo
	err = filepath.WalkDir(tmpDir, func(path string, d fs.DirEntry, err error) error {
		if err != nil {
			return err
		}
		if d.IsDir() {
			name := d.Name()
			if name == ".git" {
				return filepath.SkipDir
			}
			return nil
		}
		if filepath.Base(path) != "SKILL.md" {
			return nil
		}

		relPath, err := filepath.Rel(tmpDir, path)
		if err != nil {
			return nil
		}

		parts := strings.Split(filepath.ToSlash(relPath), "/")
		plugin := ""
		skillName := ""

		if len(parts) >= 4 && parts[0] == "plugins" {
			plugin = parts[1]
			if parts[2] == "skills" {
				skillName = parts[3]
			}
		}
		if len(parts) == 3 && parts[0] == "plugins" {
			plugin = parts[1]
			if parts[2] == "skills" {
				return nil
			}
		}

		if plugin == "" || skillName == "" {
			return nil
		}

		f, err := os.Open(path)
		if err != nil {
			return nil
		}

		scanner := bufio.NewScanner(f)
		desc := parseFrontmatterFromScanner(scanner)
		f.Close()

		content, err := os.ReadFile(path)
		if err != nil {
			return nil
		}

		skills = append(skills, skillInfo{
			Plugin:  plugin,
			Name:    skillName,
			Desc:    desc,
			RawPath: path,
			Content: content,
		})
		return nil
	})
	if err != nil {
		return nil, fmt.Errorf("扫描仓库失败: %w", err)
	}

	sort.Slice(skills, func(i, j int) bool {
		if skills[i].Plugin != skills[j].Plugin {
			return skills[i].Plugin < skills[j].Plugin
		}
		return skills[i].Name < skills[j].Name
	})

	return skills, nil
}

func displayRepoSkills(repo string, repoSkills []skillInfo) {
	fmt.Printf("%s 中的可用技能:\n\n", repo)
	type pluginGroup struct {
		Plugin string
		Skills []skillInfo
	}
	groups := make(map[string]*pluginGroup)
	for _, s := range repoSkills {
		if g, ok := groups[s.Plugin]; ok {
			g.Skills = append(g.Skills, s)
		} else {
			groups[s.Plugin] = &pluginGroup{Plugin: s.Plugin, Skills: []skillInfo{s}}
		}
	}

	pluginOrder := []string{"req", "api", "pm", "diag", "uat"}
	for _, p := range pluginOrder {
		g, ok := groups[p]
		if !ok {
			continue
		}
		fmt.Printf("  %s (%d 个技能):\n", p, len(g.Skills))
		for _, s := range g.Skills {
			fmt.Printf("    %-20s %s\n", s.Name, s.Desc)
		}
		fmt.Println()
	}

	for p, g := range groups {
		found := false
		for _, po := range pluginOrder {
			if p == po {
				found = true
				break
			}
		}
		if found {
			continue
		}
		fmt.Printf("  %s (%d 个技能):\n", p, len(g.Skills))
		for _, s := range g.Skills {
			fmt.Printf("    %-20s %s\n", s.Name, s.Desc)
		}
		fmt.Println()
	}

	fmt.Printf("\n安装示例:\n")
	fmt.Printf("  devflow-skills add %s --tool opencode --all\n", repo)
	fmt.Printf("  devflow-skills add %s --tool cursor --skill <skill-name>\n", repo)
}

func loadAllSkills() ([]skillInfo, error) {
	var skills []skillInfo
	err := fs.WalkDir(skillsFS, "plugins", func(path string, d fs.DirEntry, err error) error {
		if err != nil {
			return err
		}
		if d.IsDir() || filepath.Base(path) != "SKILL.md" {
			return nil
		}
		parts := strings.Split(filepath.ToSlash(path), "/")
		if len(parts) < 5 {
			return nil
		}
		plugin := parts[1]
		skillName := parts[3]

		f, err := skillsFS.Open(path)
		if err != nil {
			return nil
		}
		defer f.Close()

		scanner := bufio.NewScanner(f)
		desc := parseFrontmatterFromScanner(scanner)

		skills = append(skills, skillInfo{
			Plugin:  plugin,
			Name:    skillName,
			Desc:    desc,
			RawPath: path,
		})
		return nil
	})
	if err != nil {
		return nil, err
	}
	sort.Slice(skills, func(i, j int) bool {
		if skills[i].Plugin != skills[j].Plugin {
			return skills[i].Plugin < skills[j].Plugin
		}
		return skills[i].Name < skills[j].Name
	})
	return skills, nil
}

func parseFrontmatterFromScanner(scanner *bufio.Scanner) string {
	inFM := false
	fmClosed := false
	var fmLines []string

	for scanner.Scan() {
		line := scanner.Text()
		if !inFM {
			if strings.TrimSpace(line) == "---" {
				inFM = true
			} else if strings.TrimSpace(line) != "" {
				fmClosed = true
				break
			}
			continue
		}
		if strings.TrimSpace(line) == "---" {
			fmClosed = true
			break
		}
		fmLines = append(fmLines, line)
	}

	if !fmClosed {
		return ""
	}

	content := strings.Join(fmLines, "\n")
	lines := strings.Split(content, "\n")

	inDesc := false
	var descLines []string

	for _, line := range lines {
		if inDesc {
			if strings.TrimSpace(line) == "" && len(descLines) > 0 {
				descLines = append(descLines, "")
			} else if !strings.HasPrefix(line, " ") && !strings.HasPrefix(line, "\t") && line != "" {
				break
			} else {
				descLines = append(descLines, strings.TrimSpace(line))
			}
			continue
		}
		if strings.HasPrefix(line, "description:") {
			inDesc = true
			rest := strings.TrimPrefix(line, "description:")
			desc := strings.TrimSpace(rest)
			if desc != "" && desc != "|" && desc != "|-" && desc != ">" && desc != ">-" {
				return desc
			}
		}
	}

	desc := strings.TrimSpace(strings.Join(descLines, " "))
	desc = strings.Replace(desc, "\n", " ", -1)
	return desc
}

func resolveSkill(name string, allSkills []skillInfo) []skillInfo {
	parts := strings.SplitN(name, "-", 2)
	if len(parts) == 2 {
		for _, s := range allSkills {
			if s.Plugin == parts[0] && s.Name == parts[1] {
				return []skillInfo{s}
			}
		}
		return nil
	}

	var matched []skillInfo
	for _, s := range allSkills {
		if s.Name == name {
			matched = append(matched, s)
		}
	}
	return matched
}

func installSkill(cfg toolConfig, dir string, global, symlink bool, plugin, name string, content []byte) error {
	if symlink {
		return installSymlink(cfg, dir, global, plugin, name, content)
	}

	if cfg.layout == layoutHierarchical {
		return installHierarchical(cfg, dir, global, plugin, name, content)
	}
	return installFlat(cfg, dir, global, plugin, name, content)
}

func installFlat(cfg toolConfig, dir string, global bool, plugin, name string, content []byte) error {
	target := targetPath(cfg, dir, global, plugin, name)
	if err := os.MkdirAll(target, 0755); err != nil {
		return err
	}
	flatName := plugin + "-" + name
	updated := updateFrontmatterName(content, flatName)
	return os.WriteFile(filepath.Join(target, "SKILL.md"), updated, 0644)
}

func installHierarchical(cfg toolConfig, dir string, global bool, plugin, name string, content []byte) error {
	target := targetPath(cfg, dir, global, plugin, name)
	if err := os.MkdirAll(target, 0755); err != nil {
		return err
	}
	return os.WriteFile(filepath.Join(target, "SKILL.md"), content, 0644)
}

func installSymlink(cfg toolConfig, dir string, global bool, plugin, name string, content []byte) error {
	canonical := canonicalPath(dir, global, plugin, name)
	if err := os.MkdirAll(canonical, 0755); err != nil {
		return err
	}

	flatName := plugin + "-" + name
	updated := updateFrontmatterName(content, flatName)
	canonicalFile := filepath.Join(canonical, "SKILL.md")
	if err := os.WriteFile(canonicalFile, updated, 0644); err != nil {
		return err
	}

	linkTarget := targetPath(cfg, dir, global, plugin, name)
	if err := os.MkdirAll(filepath.Dir(linkTarget), 0755); err != nil {
		return err
	}

	os.Remove(linkTarget)

	linkFile := filepath.Join(linkTarget, "SKILL.md")
	os.Remove(linkFile)

	if err := os.MkdirAll(filepath.Dir(linkFile), 0755); err != nil {
		return err
	}

	relCanon, err := filepath.Rel(filepath.Dir(linkFile), canonicalFile)
	if err != nil {
		relCanon = canonicalFile
	}

	if err := os.Symlink(relCanon, linkFile); err != nil {
		return installFlat(cfg, dir, global, plugin, name, content)
	}

	return nil
}

func updateFrontmatterName(content []byte, newName string) []byte {
	lines := bytes.Split(content, []byte("\n"))
	inFM := false
	for i, line := range lines {
		trimmed := strings.TrimSpace(string(line))
		if !inFM {
			if trimmed == "---" {
				inFM = true
			}
			continue
		}
		if trimmed == "---" {
			break
		}
		if strings.HasPrefix(trimmed, "name:") {
			indent := ""
			for _, c := range string(line) {
				if c == ' ' || c == '\t' {
					indent += string(c)
				} else {
					break
				}
			}
			lines[i] = []byte(indent + "name: " + newName)
			break
		}
	}
	return bytes.Join(lines, []byte("\n"))
}

func pluginLabel(p string) string {
	return p
}

type skillsFlag []string

func (s *skillsFlag) String() string {
	return strings.Join(*s, ", ")
}

func (s *skillsFlag) Set(v string) error {
	*s = append(*s, v)
	return nil
}
