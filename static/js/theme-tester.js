/**
 * Theme Color Testing Utility
 * 
 * Usage in browser console:
 * 1. Copy and paste this entire file into the console
 * 2. Call: testTheme({ brightness: 1.2, contrast: 1.1 })
 * 3. Experiment with different values
 * 4. Copy the generated CSS to your styles.css
 */

// Utility: Convert HEX to OKLCH
function hexToOklch(hex) {
  // Remove # if present
  hex = hex.replace('#', '');
  
  // Convert to RGB
  const r = parseInt(hex.substr(0, 2), 16) / 255;
  const g = parseInt(hex.substr(2, 2), 16) / 255;
  const b = parseInt(hex.substr(4, 2), 16) / 255;
  
  // Convert RGB to Linear RGB
  const toLinear = (c) => {
    return c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
  };
  
  const rLin = toLinear(r);
  const gLin = toLinear(g);
  const bLin = toLinear(b);
  
  // Convert to XYZ (D65 illuminant)
  const x = 0.4124564 * rLin + 0.3575761 * gLin + 0.1804375 * bLin;
  const y = 0.2126729 * rLin + 0.7151522 * gLin + 0.0721750 * bLin;
  const z = 0.0193339 * rLin + 0.1191920 * gLin + 0.9503041 * bLin;
  
  // Convert XYZ to Lab (simplified OKLAB approximation)
  const l = Math.cbrt(y);
  const a = (Math.cbrt(x) - Math.cbrt(y)) * 0.4;
  const bVal = (Math.cbrt(y) - Math.cbrt(z)) * 0.4;
  
  // Convert to LCH
  const lightness = l * 100;
  const chroma = Math.sqrt(a * a + bVal * bVal);
  let hue = Math.atan2(bVal, a) * 180 / Math.PI;
  if (hue < 0) hue += 360;
  
  return {
    l: Math.round(lightness * 100) / 100,
    c: Math.round(chroma * 100) / 100,
    h: Math.round(hue * 100) / 100
  };
}

// Utility: Parse OKLCH string
function parseOklch(oklchString) {
  const match = oklchString.match(/oklch\(([\d.]+)%?\s+([\d.]+)\s+([\d.]+)\)/);
  if (!match) return null;
  
  return {
    l: parseFloat(match[1]),
    c: parseFloat(match[2]),
    h: parseFloat(match[3])
  };
}

// Utility: Format OKLCH for CSS
function formatOklch(l, c, h) {
  return `oklch(${l}% ${c.toFixed(2)} ${h.toFixed(0)})`;
}

// Main theme testing function
function testTheme(options = {}) {
  const {
    brightness = 1.0,  // 0.5 to 1.5 recommended
    contrast = 1.0,    // 0.5 to 1.5 recommended
    hueDrift = 0       // -30 to 30 recommended
  } = options;
  
  console.log('🎨 Testing Theme Colors');
  console.log('━'.repeat(60));
  console.log(`Brightness: ${brightness}x | Contrast: ${contrast}x | Hue Drift: ${hueDrift}°`);
  console.log('━'.repeat(60));
  
  // Original colors
  const colors = {
    primary: '#7643bd',
    secondary: '#008dbe',
    accent: 'oklch(65% 0.25 185)',
    neutral: 'oklch(50% 0.05 265)',
    info: '#5b8bb5',
    success: 'oklch(65% 0.22 145)',
    warning: '#F7C13C',
    error: 'oklch(65% 0.35 28)'
  };
  
  const adjustedColors = {};
  const cssOutput = [];
  
  // Process each color
  Object.entries(colors).forEach(([name, value]) => {
    let oklch;
    
    // Convert HEX to OKLCH if needed
    if (value.startsWith('#')) {
      oklch = hexToOklch(value);
    } else {
      oklch = parseOklch(value);
    }
    
    if (!oklch) {
      console.error(`Failed to parse color: ${name}`);
      return;
    }
    
    // Apply adjustments
    let adjustedL = oklch.l * brightness;
    let adjustedC = oklch.c * contrast;
    let adjustedH = oklch.h + hueDrift;
    
    // Clamp values
    adjustedL = Math.max(0, Math.min(100, adjustedL));
    adjustedC = Math.max(0, adjustedC);
    adjustedH = adjustedH % 360;
    if (adjustedH < 0) adjustedH += 360;
    
    const adjustedColor = formatOklch(adjustedL, adjustedC, adjustedH);
    adjustedColors[name] = adjustedColor;
    
    // Log to console with color preview
    console.log(
      `%c ${name.toUpperCase().padEnd(12)} %c ${value.padEnd(25)} → ${adjustedColor}`,
      `background: ${value}; color: white; padding: 2px 8px; border-radius: 3px;`,
      'padding: 2px 0;'
    );
    
    // Build CSS output
    cssOutput.push(`  --color-${name}: ${adjustedColor};`);
  });
  
  console.log('━'.repeat(60));
  console.log('\n📋 Copy this CSS to your styles.css:\n');
  console.log(cssOutput.join('\n'));
  console.log('\n');
  
  // Apply to document (temporary preview)
  const root = document.documentElement;
  Object.entries(adjustedColors).forEach(([name, value]) => {
    root.style.setProperty(`--color-${name}`, value);
  });
  
  console.log('✅ Colors applied to page! Refresh to reset.');
  
  return adjustedColors;
}

// Preset configurations
function presets() {
  console.log('🎨 Available Presets:\n');
  console.log('testTheme({ brightness: 1.2, contrast: 1.0 })  // Lighter');
  console.log('testTheme({ brightness: 0.8, contrast: 1.0 })  // Darker');
  console.log('testTheme({ brightness: 1.0, contrast: 1.3 })  // More vibrant');
  console.log('testTheme({ brightness: 1.0, contrast: 0.7 })  // More muted');
  console.log('testTheme({ brightness: 1.1, contrast: 1.2, hueDrift: 10 })  // Warmer');
  console.log('testTheme({ brightness: 1.1, contrast: 1.2, hueDrift: -10 }) // Cooler');
  console.log('\nOr combine multiple adjustments:');
  console.log('testTheme({ brightness: 1.15, contrast: 1.1, hueDrift: 5 })');
}

// Quick reset function
function resetTheme() {
  const root = document.documentElement;
  const originalColors = {
    primary: '#7643bd',
    secondary: '#008dbe',
    accent: 'oklch(65% 0.25 185)',
    neutral: 'oklch(50% 0.05 265)',
    info: '#5b8bb5',
    success: 'oklch(65% 0.22 145)',
    warning: '#F7C13C',
    error: 'oklch(65% 0.35 28)'
  };
  
  Object.entries(originalColors).forEach(([name, value]) => {
    root.style.setProperty(`--color-${name}`, value);
  });
  
  console.log('✅ Theme reset to original colors');
}

// Export for easy access
console.log('━'.repeat(60));
console.log('🎨 THEME COLOR TESTER LOADED');
console.log('━'.repeat(60));
console.log('\nQuick Start:');
console.log('  testTheme()           - Test current theme');
console.log('  presets()             - Show preset examples');
console.log('  resetTheme()          - Reset to original colors');
console.log('\nCustom adjustments:');
console.log('  testTheme({ brightness: 1.2, contrast: 1.1, hueDrift: 5 })');
console.log('━'.repeat(60));
