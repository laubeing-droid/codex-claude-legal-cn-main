/**
 * svg2png.js
 * 高保真 SVG → PNG 转换脚本
 * 支持 emoji、中文、CSS；自动根据 viewBox 渲染；无裁切。
 *
 * 重要特性：PNG文件**总是**生成到SVG源文件所在目录，确保位置统一
 */

import fs from "fs";
import path from "path";
import puppeteer from "puppeteer";

async function svgToPng(inputPath, outputPath, dpi = 600) {
  if (!fs.existsSync(inputPath)) {
    throw new Error(`输入文件不存在: ${inputPath}`);
  }

  const svgContent = fs.readFileSync(inputPath, "utf8");
  // 尝试使用系统 Chrome
const findChrome = () => {
  const possiblePaths = [
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/Applications/Chromium.app/Contents/MacOS/Chromium',
    '/usr/bin/google-chrome-stable',
    '/usr/bin/chromium-browser',
    '/usr/bin/google-chrome'
  ];

  for (const path of possiblePaths) {
    if (fs.existsSync(path)) {
      return path;
    }
  }
  return undefined;
};

const browser = await puppeteer.launch({
    headless: "new", // 使用新的 headless 模式
    args: [
      "--no-sandbox",
      "--disable-setuid-sandbox",
      "--disable-dev-shm-usage",
      "--disable-accelerated-2d-canvas",
      "--no-first-run",
      "--no-zygote",
      "--disable-gpu",
      "--disable-extensions",
      "--disable-background-timer-throttling",
      "--disable-backgrounding-occluded-windows",
      "--disable-renderer-backgrounding",
      "--disable-features=TranslateUI",
      "--disable-ipc-flooding-protection",
      "--enable-features=NetworkService,NetworkServiceInProcess"
    ],
    executablePath: findChrome(), // 尝试使用系统 Chrome
  });

  const page = await browser.newPage();
  await page.setContent(svgContent, { waitUntil: "networkidle0" });

  // 自动计算 SVG 尺寸
  const dimensions = await page.evaluate(() => {
    const svg = document.querySelector("svg");
    if (!svg) throw new Error("未找到 <svg> 元素");
    const vb = svg.viewBox.baseVal;
    const w = svg.getAttribute("width");
    const h = svg.getAttribute("height");
    return {
      width: w ? parseFloat(w) : vb.width || 800,
      height: h ? parseFloat(h) : vb.height || 600,
    };
  });

  // 计算设备像素比例以实现指定DPI
  // 标准屏幕DPI为96，计算缩放因子
  const scaleFactor = dpi / 96;
  
  // 设置页面视窗以支持高DPI输出
  await page.setViewport({
    width: Math.round(dimensions.width),
    height: Math.round(dimensions.height),
    deviceScaleFactor: scaleFactor, // 根据目标DPI设置缩放因子
  });

  const element = await page.$("svg");
  if (!element) throw new Error("SVG元素未加载");

  await element.screenshot({
    path: outputPath,
    omitBackground: true,
  });

  await browser.close();
  console.log(`✅ 已生成 PNG (${dpi} DPI): ${outputPath}`);
  console.log(`📏 输出尺寸: ${Math.round(dimensions.width * scaleFactor)}x${Math.round(dimensions.height * scaleFactor)} 像素`);
}

// CLI入口
const [,, inputFile, outputFileArg, dpiArg] = process.argv;
if (!inputFile) {
  console.error("用法: node svg2png.js input.svg [output.png] [dpi]");
  console.error("示例: node svg2png.js input.svg output.png 600");
  console.error("默认DPI: 600");
  process.exit(1);
}

// 强制策略：PNG图片**必须**生成到SVG源文件所在目录
// 无论是否提供outputFileArg，都忽略其目录部分，只使用文件名
const svgDir = path.dirname(inputFile);
const pngFileName = outputFileArg
  ? path.basename(outputFileArg, ".png") + ".png"  // 提取文件名，忽略路径
  : path.basename(inputFile, ".svg") + ".png";    // 默认使用SVG文件名
const outputFile = path.join(svgDir, pngFileName);

const dpi = dpiArg ? parseInt(dpiArg) : 600;

// 记录生成位置信息
console.log(`📁 SVG源目录: ${svgDir}`);
if (outputFileArg && path.dirname(outputFileArg) !== svgDir) {
  console.log(`⚠️  忽略指定的输出目录，强制使用SVG源目录`);
}

if (dpi < 72 || dpi > 2400) {
  console.error("❌ DPI值应在72-2400之间");
  process.exit(1);
}

console.log(`🎯 目标DPI: ${dpi} (缩放因子: ${(dpi/96).toFixed(2)}x)`);

svgToPng(inputFile, outputFile, dpi).catch((err) => {
  console.error("❌ 转换失败:", err);
  process.exit(1);
});
