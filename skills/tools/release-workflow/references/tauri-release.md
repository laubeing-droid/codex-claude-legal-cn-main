# Tauri 桌面应用发布指南

基于 Tauri v2 的桌面应用发布特有事项。

## CI 工作流配置

推荐使用 `tauri-apps/tauri-action`，分离 build 和 publish 两个 job：

```yaml
name: release

on:
 push:
 tags:
 - 'v*'

permissions:
 contents: write

concurrency:
 group: release-${{ github.ref_name }}
 cancel-in-progress: true

jobs:
 build:
 strategy:
 fail-fast: false
 matrix:
 include:
 - platform: macos-latest
 args: --target aarch64-apple-darwin
 - platform: macos-latest
 args: --target x86_64-apple-darwin
 - platform: windows-latest
 args: ''
 runs-on: ${{ matrix.platform }}
 steps:
 - uses: actions/checkout@v4

 - uses: pnpm/action-setup@v4
 with:
 version: 10

 - uses: dtolnay/rust-toolchain@stable
 with:
 targets: ${{ matrix.platform == 'macos-latest' && 'aarch64-apple-darwin,x86_64-apple-darwin' || '' }}

 - uses: Swatinem/rust-cache@v2
 with:
 workdir: src-tauri

 - run: pnpm install

 - uses: tauri-apps/tauri-action@v0
 env:
 GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
 # 仅自动更新需要：签名密钥
 TAURI_SIGNING_PRIVATE_KEY: ${{ secrets.TAURI_SIGNING_PRIVATE_KEY }}
 TAURI_SIGNING_PRIVATE_KEY_PASSWORD: ${{ secrets.TAURI_SIGNING_PRIVATE_KEY_PASSWORD }}
 with:
 tagName: ${{ github.ref_name }}
 releaseName: 'App ${{ github.ref_name }}'
 releaseDraft: true
 prerelease: false
 # 不用自动更新时设为 false，用自动更新时设为 true
 includeUpdaterJson: false
 args: ${{ matrix.args }}

 # 仅自动更新需要此 job：生成 latest.json 并发布
 publish:
 needs: build
 runs-on: ubuntu-latest
 steps:
 - uses: actions/checkout@v4
 - name: Generate latest.json
 run: |
 # 从 draft release 下载 .sig 文件，生成 latest.json
 - name: Upload and publish
 run: |
 gh release upload "${{ github.ref_name }}" latest.json --clobber
 gh release edit "${{ github.ref_name }}" --draft=false
```

## 配置要点

### 包管理器

跨平台构建（macOS + Windows）推荐 pnpm。npm/bun 存在 optional dependencies bug，macOS lock file 不包含 Windows 原生绑定。

仅构建 macOS 时 `npm ci` 可用，但统一使用 pnpm 可避免后续扩展 Windows 矩阵时踩坑。

### includeUpdaterJson

`includeUpdaterJson: false` + 手动生成 `latest.json` 可精确控制平台键名和 URL 格式，避免 tauri-action 内置生成器产生冗余键。

### 分离 build 和 publish

单 job 模式无法在发布前验证所有平台构建成功，也无法在发布前自定义 `latest.json`。build job 上传到 draft release，publish job 在全部成功后发布。

### concurrency

移动 tag 会触发重复构建，添加 `concurrency` 配置避免。

## 构建产物

### 仅安装包（不需要自动更新）

Pake 等项目只发布安装包，不包含更新器产物。适用于用户手动下载更新的场景。

| 平台 | 安装包 |
|------|--------|
| macOS ARM | `App_X.Y.Z_aarch64.dmg` |
| macOS Intel | `App_X.Y.Z_x64.dmg` |
| Windows | `App_X.Y.Z_x64-setup.exe` |

### 带自动更新

lencx/ChatGPT 等项目在安装包之外，还包含更新器所需的产物。更新器通过 `latest.json` 检查版本、下载对应平台 bundle、用 `.sig` 验证完整性。

| 平台 | 安装包 | 更新器产物 | 签名 |
|------|--------|-----------|------|
| macOS ARM | `App_X.Y.Z_aarch64.dmg` | `App_aarch64.app.tar.gz` | `.sig` |
| macOS Intel | `App_X.Y.Z_x64.dmg` | `App_x64.app.tar.gz` | `.sig` |
| Windows | `App_X.Y.Z_x64-setup.exe` | — | `.exe.sig` |

Windows 只需 `.exe`（NSIS），不需要额外发布 `.msi`。签名文件 `.sig` 和 `latest.json` 一起放在 release assets 中，更新端点直接用 GitHub 直链：

```
https://github.com/<owner>/<repo>/releases/latest/download/latest.json
```

## latest.json 格式

Tauri updater 需要一个 `latest.json`，包含版本号、签名和各平台下载 URL。

```json
{
 "version": "X.Y.Z",
 "notes": "发布说明",
 "pub_date": "2026-05-20T00:00:00Z",
 "platforms": {
 "darwin-aarch64": { "signature": "...", "url": "..." },
 "darwin-x86_64": { "signature": "...", "url": "..." },
 "windows-x86_64": { "signature": "...", "url": "..." }
 }
}
```

平台键名必须使用标准格式（`darwin-aarch64` / `darwin-x86_64` / `windows-x86_64`），避免 `darwin-aarch64-app` 等非标准键名。

## 国内镜像同步

目标用户包含国内用户时，可在 publish job 中同步到 Gitee：创建 Gitee Release → 上传构建产物 → 生成 Gitee 专属 `latest.json` → 上传。

需要 GitHub Secrets：`GITEE_TOKEN`、`GITEE_OWNER`。

Gitee 没有 `releases/latest/download/` 直链，作为 updater endpoint 前需验证可访问性。
