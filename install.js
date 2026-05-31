#!/usr/bin/env node

const { spawnSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const os = require('os');

const VERSION = require('./package.json').version;

// ── tool config ─────────────────────────────────────────────────────────

const TOOLS = {
  opencode:  { projectSkillsDir: '.agents/skills',         globalSkillsDir: '.config/opencode/skills',    flat: true },
  codex:     { projectSkillsDir: '.agents/skills',         globalSkillsDir: '.config/codex/skills',       flat: true },
  claude:    { projectSkillsDir: 'plugins',                globalSkillsDir: 'plugins',                    flat: false },
  cursor:    { projectSkillsDir: '.agents/skills',         globalSkillsDir: '.cursor/skills',             flat: true },
  copilot:   { projectSkillsDir: '.agents/skills',         globalSkillsDir: '.github/copilot/skills',     flat: true },
  codebuddy: { projectSkillsDir: '.agents/skills',         globalSkillsDir: '.config/codebuddy/skills',   flat: true },
  windsurf:  { projectSkillsDir: '.agents/skills',         globalSkillsDir: '.config/windsurf/skills',    flat: true },
};

const PLUGIN_ORDER = ['req', 'api', 'pm', 'diag', 'uat'];

// ── helpers ─────────────────────────────────────────────────────────────

function usage() {
  console.log(`devflow-skills v${VERSION} — AI 技能一键安装/管理工具

用法:
  devflow-skills install   --tool <TOOL> [--skill <NAME>...] [--all] [--plugin <NAME>] [--dir <PATH>] [--global] [--symlink]
  devflow-skills list      [--plugin <NAME>] [--format text|json] [--filter <STR>]
  devflow-skills uninstall --tool <TOOL> [--skill <NAME>...] [--all] [--dir <PATH>] [--global]
  devflow-skills add       <owner/repo> [--tool <TOOL>] [--skill <NAME>...] [--all] [--list] [--dir <PATH>] [--global] [--symlink]

命令:
  install     安装技能到目标 AI 工具目录
  list        列出所有可用技能
  uninstall   从目标 AI 工具目录卸载技能
  add         从 GitHub 仓库克隆并安装技能

支持的 --tool 值: ${Object.keys(TOOLS).join(', ')}

示例:
  npx devflow-skills install --tool opencode --all
  npx devflow-skills install --tool cursor --skill req-dev
  npx devflow-skills install --tool opencode --all -g
  npx devflow-skills install --tool cursor --all --symlink
  npx devflow-skills list --plugin req
  npx devflow-skills list --filter dev
  npx devflow-skills uninstall --tool opencode --all
  npx devflow-skills add zhouhao4221/devflow-skills --tool copilot --all
  npx devflow-skills add zhouhao4221/devflow-skills --list
`);
}

function fail(msg) {
  console.error('错误:', msg);
  process.exit(1);
}

function ensure(cond, msg) {
  if (!cond) fail(msg);
}

function parseArgs(argv) {
  const positional = [];
  const flags = {};
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '-g') {
      flags.global = true;
      continue;
    }
    if (!a.startsWith('--')) { positional.push(a); continue; }

    const eq = a.indexOf('=');
    const key = eq > -1 ? a.slice(2, eq) : a.slice(2);
    let val = true;
    if (eq > -1) {
      val = a.slice(eq + 1);
    } else if (i + 1 < argv.length && !argv[i + 1].startsWith('-')) {
      val = argv[++i];
    }

    if (flags[key] === undefined) {
      flags[key] = val;
    } else if (Array.isArray(flags[key])) {
      flags[key].push(val);
    } else {
      flags[key] = [flags[key], val];
    }
  }
  // normalize single-element arrays
  if (flags.skill !== undefined && !Array.isArray(flags.skill)) flags.skill = [flags.skill];
  return { positional, flags };
}

function requireTool(flags) {
  ensure(flags.tool, '--tool 是必需参数');
  const cfg = TOOLS[flags.tool];
  ensure(cfg, `不支持的 --tool: ${flags.tool} (支持: ${Object.keys(TOOLS).join(', ')})`);
  return cfg;
}

function requireSelection(flags) {
  const hasAll = !!flags.all;
  const hasSkill = !!(flags.skill && flags.skill.length > 0);
  const hasPlugin = !!flags.plugin;
  ensure(hasAll || hasSkill || hasPlugin, '请指定 --skill、--plugin 或 --all');
  ensure(!(hasAll && hasSkill), '--skill 与 --all 不能同时使用');
}

// ── frontmatter ─────────────────────────────────────────────────────────

function parseFrontmatter(content) {
  const lines = content.split('\n');
  if (lines[0].trim() !== '---') return { name: '', description: '' };
  const end = lines.indexOf('---', 1);
  if (end === -1) return { name: '', description: '' };

  const fm = {};
  let curKey = '';
  for (const line of lines.slice(1, end)) {
    const m = line.match(/^(\w[\w-]*):\s*(.*)/);
    if (m) {
      curKey = m[1];
      const after = m[2].trim();
      fm[curKey] = (after === '|' || after === '>' || after === '|-' || after === '>-') ? '' : after;
    } else if (curKey) {
      const trimmed = line.trimStart();
      if (trimmed && line.length - trimmed.length >= 2) {
        fm[curKey] = fm[curKey] ? fm[curKey] + ' ' + trimmed : trimmed;
      }
    }
  }
  return { name: fm.name || '', description: (fm.description || '').replace(/\n/g, ' ').trim() };
}

function updateFrontmatterName(content, newName) {
  return content.replace(/^name:\s*.*/m, 'name: ' + newName);
}

// ── skill loading ───────────────────────────────────────────────────────

function loadSkills(baseDir) {
  const skills = [];
  const pluginsDir = path.join(baseDir, 'plugins');
  if (!fs.existsSync(pluginsDir)) return skills;

  for (const plugin of fs.readdirSync(pluginsDir)) {
    const skillsDir = path.join(pluginsDir, plugin, 'skills');
    if (!fs.existsSync(skillsDir)) continue;
    for (const name of fs.readdirSync(skillsDir)) {
      const file = path.join(skillsDir, name, 'SKILL.md');
      if (!fs.existsSync(file)) continue;
      const raw = fs.readFileSync(file, 'utf-8');
      const fm = parseFrontmatter(raw);
      skills.push({ plugin, name, description: fm.description, file, raw });
    }
  }
  skills.sort((a, b) => a.plugin.localeCompare(b.plugin) || a.name.localeCompare(b.name));
  return skills;
}

function resolveSkill(spec, allSkills) {
  const parts = spec.split('-', 2);
  if (parts.length === 2) {
    const m = allSkills.find(s => s.plugin === parts[0] && s.name === parts[1]);
    return m ? [m] : [];
  }
  return allSkills.filter(s => s.name === spec);
}

function uniqueResolve(spec, allSkills) {
  const matched = resolveSkill(spec, allSkills);
  ensure(matched.length > 0, `未找到技能 '${spec}'，使用 'devflow-skills list' 查看所有可用技能`);
  if (matched.length > 1) {
    for (const s of matched) console.error(`  ${s.plugin}-${s.name}: ${s.description}`);
    fail(`技能名 '${spec}' 匹配到多个技能，请使用完整的扁平名 (如 req-dev) 来区分`);
  }
  return matched[0];
}

function selectSkills(flags, allSkills) {
  if (flags.all) return allSkills;
  if (flags.plugin) {
    const s = allSkills.filter(s => s.plugin === flags.plugin);
    ensure(s.length > 0, `未找到插件 '${flags.plugin}' 的技能`);
    return s;
  }
  return flags.skill.map(s => uniqueResolve(s, allSkills));
}

// ── target paths ────────────────────────────────────────────────────────

function targetBase(cfg, dir, global) {
  return global ? path.join(os.homedir(), cfg.globalSkillsDir) : path.join(dir, cfg.projectSkillsDir);
}

function targetPath(cfg, dir, global, plugin, name) {
  const base = targetBase(cfg, dir, global);
  return cfg.flat ? path.join(base, plugin + '-' + name) : path.join(base, plugin, 'skills', name);
}

function canonicalBase(dir, global) {
  return global ? path.join(os.homedir(), '.agents', 'skills') : path.join(dir, '.agents', 'skills');
}

function canonicalPath(dir, global, plugin, name) {
  return path.join(canonicalBase(dir, global), plugin + '-' + name);
}

// ── install ─────────────────────────────────────────────────────────────

function installOne(cfg, dir, global, symlink, { plugin, name, raw }) {
  if (symlink) return installSymlink(cfg, dir, global, plugin, name, raw);

  const dest = targetPath(cfg, dir, global, plugin, name);
  fs.mkdirSync(dest, { recursive: true });
  const content = cfg.flat ? updateFrontmatterName(raw, plugin + '-' + name) : raw;
  fs.writeFileSync(path.join(dest, 'SKILL.md'), content);
}

function installSymlink(cfg, dir, global, plugin, name, raw) {
  const canonDir = canonicalPath(dir, global, plugin, name);
  fs.mkdirSync(canonDir, { recursive: true });
  const flatName = plugin + '-' + name;
  const updated = cfg.flat ? updateFrontmatterName(raw, flatName) : raw;
  fs.writeFileSync(path.join(canonDir, 'SKILL.md'), updated);

  const linkDir = targetPath(cfg, dir, global, plugin, name);
  const linkFile = path.join(linkDir, 'SKILL.md');
  try { fs.unlinkSync(linkDir); } catch (_) {}
  try { fs.unlinkSync(linkFile); } catch (_) {}
  fs.mkdirSync(path.dirname(linkFile), { recursive: true });

  try {
    fs.symlinkSync(path.relative(path.dirname(linkFile), path.join(canonDir, 'SKILL.md')), linkFile);
  } catch (_) {
    installOne(cfg, dir, global, false, { plugin, name, raw });
  }
}

function installAll(selected, cfg, dir, global, symlink, sourceLabel) {
  let installed = 0;
  const quiet = selected.length > 10;
  for (const s of selected) {
    try {
      installOne(cfg, dir, global, symlink, s);
      installed++;
      if (!quiet || installed <= 10) console.log(`  ${s.plugin}-${s.name} (${s.description})`);
      else if (installed === 11) console.log('  ...');
    } catch (e) {
      console.error(`安装 ${s.plugin}-${s.name} 失败:`, e.message);
    }
  }
  const label = sourceLabel ? `从 ${sourceLabel} ` : '';
  console.log(`\n已${label}安装 ${installed} 个技能到 ${targetBase(cfg, dir, global)}/`);
  console.log('下一步: 重启 AI 工具或刷新技能列表即可使用。');
}

function runInstall(flags) {
  const cfg = requireTool(flags);
  requireSelection(flags);
  const selected = selectSkills(flags, loadSkills(__dirname));
  installAll(selected, cfg, flags.dir || '.', !!flags.global, !!flags.symlink);
}

// ── list ────────────────────────────────────────────────────────────────

function groupSkills(skills) {
  const groups = {};
  for (const s of skills) {
    if (!groups[s.plugin]) groups[s.plugin] = [];
    groups[s.plugin].push(s);
  }
  return groups;
}

function sortedPlugins(groups, filterPlugin) {
  const order = filterPlugin ? [filterPlugin] : [...PLUGIN_ORDER];
  for (const p of Object.keys(groups).sort()) {
    if (!order.includes(p)) order.push(p);
  }
  return order;
}

function printSkillTable(plugins, groups, indent) {
  for (const p of plugins) {
    if (!groups[p]) continue;
    console.log(`${indent}${p} (${groups[p].length} 个技能):`);
    for (const s of groups[p]) console.log(`${indent}  ${s.name.padEnd(20)} ${s.description}`);
    console.log();
  }
}

function runList(flags) {
  let skills = loadSkills(__dirname);
  if (flags.plugin) skills = skills.filter(s => s.plugin === flags.plugin);
  if (flags.filter) {
    const f = flags.filter.toLowerCase();
    skills = skills.filter(s => (s.plugin + '-' + s.name).includes(f) || s.name.includes(f));
  }

  if (flags.format === 'json') {
    const out = {};
    for (const p of sortedPlugins(groupSkills(skills), flags.plugin)) {
      const g = groupSkills(skills)[p];
      if (!g) continue;
      out[p] = g.map(s => ({ name: s.name, flatName: s.plugin + '-' + s.name, description: s.description }));
    }
    console.log(JSON.stringify(out, null, 2));
    return;
  }

  const groups = groupSkills(skills);
  for (const p of sortedPlugins(groups, flags.plugin)) {
    if (!groups[p]) continue;
    console.log(`${p} 插件 (${groups[p].length} 个技能):`);
    for (const s of groups[p]) console.log(`  ${(s.plugin + '-' + s.name).padEnd(22)} ${s.description}`);
    console.log();
  }
}

// ── uninstall ───────────────────────────────────────────────────────────

function runUninstall(flags) {
  const cfg = requireTool(flags);
  const dir = flags.dir || '.';
  const global = !!flags.global;

  if (flags.all) {
    const base = targetBase(cfg, dir, global);
    const abs = path.resolve(base);
    if (!fs.existsSync(abs)) { console.log(`技能目录不存在: ${abs}\n无需卸载。`); return; }
    fs.rmSync(abs, { recursive: true });
    console.log(`已卸载所有技能，删除目录: ${abs}`);

    const canon = canonicalBase(dir, global);
    if (fs.existsSync(canon)) console.error(`注意: 规范目录 ${canon} 仍存在，如使用过 --symlink 模式可能需要手动清理`);
    return;
  }

  ensure(flags.skill && flags.skill.length > 0, '请指定 --skill 或 --all');

  const allSkills = loadSkills(__dirname);
  let removed = 0;
  for (const spec of flags.skill) {
    const parts = spec.split('-', 2);
    let plugin, name;
    if (parts.length === 2) { plugin = parts[0]; name = parts[1]; }
    else {
      const s = uniqueResolve(spec, allSkills);
      plugin = s.plugin; name = s.name;
    }

    const tgt = targetPath(cfg, dir, global, plugin, name);
    if (!fs.existsSync(tgt)) { console.log(`未安装: ${plugin}-${name}`); continue; }
    try {
      fs.rmSync(tgt, { recursive: true });
      console.log(`已卸载: ${plugin}-${name}`);
      removed++;
    } catch (e) {
      console.error(`卸载 ${plugin}-${name} 失败:`, e.message);
    }
  }

  console.log(removed === 0 ? '没有需要卸载的技能。' : `\n已卸载 ${removed} 个技能。`);
}

// ── add ─────────────────────────────────────────────────────────────────

function fetchRepoSkills(repo) {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'devflow-skills-'));
  const url = `https://github.com/${repo}.git`;

  console.error(`正在克隆 ${url}...`);
  const r = spawnSync('git', ['clone', '--depth', '1', url, tmpDir], { stdio: 'inherit' });
  if (r.status !== 0) {
    try { fs.rmSync(tmpDir, { recursive: true }); } catch (_) {}
    fail('git clone 失败');
  }

  const skills = loadSkills(tmpDir);
  try { fs.rmSync(tmpDir, { recursive: true }); } catch (_) {}
  return skills;
}

function runAdd(flags, positional) {
  const repo = positional[0];
  ensure(repo, '请指定仓库 (格式: owner/repo)\n示例: devflow-skills add zhouhao4221/devflow-skills --list');
  ensure(repo.includes('/'), '仓库格式无效，请使用 owner/repo 格式');

  if (flags.list) {
    const skills = fetchRepoSkills(repo);
    console.log(`${repo} 中的可用技能:\n`);
    printSkillTable(sortedPlugins(groupSkills(skills)), groupSkills(skills), '  ');
    console.log(`安装示例:`);
    console.log(`  devflow-skills add ${repo} --tool opencode --all`);
    console.log(`  devflow-skills add ${repo} --tool cursor --skill <skill-name>`);
    return;
  }

  const cfg = requireTool(flags);
  requireSelection(flags);
  const selected = selectSkills(flags, fetchRepoSkills(repo));
  installAll(selected, cfg, flags.dir || '.', !!flags.global, !!flags.symlink, repo);
}

// ── version ─────────────────────────────────────────────────────────────

function runVersion() {
  console.log(`devflow-skills v${VERSION}`);
}

// ── main ────────────────────────────────────────────────────────────────

function main() {
  const argv = process.argv.slice(2);
  if (argv.length === 0) { usage(); process.exit(1); }

  const cmd = argv[0];
  const rest = argv.slice(1);

  if (cmd === 'help' || cmd === '-h' || cmd === '--help') { usage(); return; }
  if (cmd === 'version' || cmd === '--version' || cmd === '-v') { runVersion(); return; }

  const { positional, flags } = parseArgs(rest);

  switch (cmd) {
    case 'install':   return runInstall(flags);
    case 'list':      return runList(flags);
    case 'uninstall': return runUninstall(flags);
    case 'add':       return runAdd(flags, positional);
    default:
      console.error(`未知命令: ${cmd}\n`);
      usage();
      process.exit(1);
  }
}

main();
