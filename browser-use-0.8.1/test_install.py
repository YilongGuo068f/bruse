import browser_use
import playwright
import sys
import pkg_resources

print("✓ browser-use 已成功导入")
print("✓ playwright 已成功导入")
print("✓ Python version:", sys.version.split()[0])

# Check installed versions
try:
    browser_use_version = pkg_resources.get_distribution("browser-use").version
    print("✓ browser-use version:", browser_use_version)
except:
    pass

try:
    playwright_version = pkg_resources.get_distribution("playwright").version
    print("✓ playwright version:", playwright_version)
except:
    pass

print("\n✅ 环境配置成功!")
