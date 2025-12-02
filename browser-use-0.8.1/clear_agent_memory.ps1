# ============================================
# 清理 Browser-Use Agent 记忆脚本
# ============================================
# 用途：清除 Agent 保存的文件和记忆，避免污染下次运行
# 使用：.\clear_agent_memory.ps1

Write-Host "🧹 开始清理 Agent 记忆..." -ForegroundColor Yellow

# 清理 Agent 保存的文件
$agentDataPath = "agent_output\browseruse_agent_data"
if (Test-Path $agentDataPath) {
    Write-Host "   清理: $agentDataPath" -ForegroundColor Cyan
    Remove-Item -Path "$agentDataPath\*" -Force -Recurse -ErrorAction SilentlyContinue
    Write-Host "   ✅ 已清理 Agent 数据" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  目录不存在: $agentDataPath" -ForegroundColor Yellow
}

# 清理下载文件（可选）
$downloadsPath = "downloads"
if (Test-Path $downloadsPath) {
    $fileCount = (Get-ChildItem -Path $downloadsPath -File).Count
    if ($fileCount -gt 0) {
        Write-Host "   发现 $fileCount 个下载文件" -ForegroundColor Cyan
        $confirm = Read-Host "   是否清理下载文件？(y/N)"
        if ($confirm -eq 'y' -or $confirm -eq 'Y') {
            Remove-Item -Path "$downloadsPath\*" -Force -Recurse -ErrorAction SilentlyContinue
            Write-Host "   ✅ 已清理下载文件" -ForegroundColor Green
        } else {
            Write-Host "   ⏭️  跳过清理下载文件" -ForegroundColor Yellow
        }
    }
}

Write-Host "`n✅ 清理完成！现在可以运行新任务了。" -ForegroundColor Green
Write-Host "   运行: python my_custom_template.py`n" -ForegroundColor Cyan
