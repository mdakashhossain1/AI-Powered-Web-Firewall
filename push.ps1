# AI-Powered Web Firewall - GitHub Upload Script (PowerShell)
# Author: Akash Hossain (arknox.in)
# License: MIT

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  AI-Powered Web Firewall - GitHub Upload" -ForegroundColor White
Write-Host "  Author: Akash Hossain (arknox.in)" -ForegroundColor Yellow
Write-Host "  License: MIT" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Git is installed
Write-Host "Checking Git installation..." -ForegroundColor Blue
try {
    $gitVersion = git --version 2>$null
    Write-Host "✅ Git is installed: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ ERROR: Git is not installed or not in PATH" -ForegroundColor Red
    Write-Host ""
    Write-Host "📥 SOLUTION: Please install Git first" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. Download Git from: https://git-scm.com/download/windows" -ForegroundColor White
    Write-Host "2. Install Git with default settings" -ForegroundColor White
    Write-Host "3. Restart PowerShell" -ForegroundColor White
    Write-Host "4. Run this script again" -ForegroundColor White
    Write-Host ""
    Write-Host "🔧 Alternative: Use GitHub Desktop" -ForegroundColor Cyan
    Write-Host "   Download from: https://desktop.github.com/" -ForegroundColor White
    Write-Host ""
    $choice = Read-Host "Press 'Y' to open Git download page, or any other key to exit"
    if ($choice -eq 'Y' -or $choice -eq 'y') {
        Start-Process "https://git-scm.com/download/windows"
    }
    exit 1
}

# Initialize Git repository
Write-Host "[1/8] Initializing Git repository..." -ForegroundColor Blue
try {
    git init
    Write-Host "✅ Git repository initialized" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to initialize Git repository" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Create .gitignore if it doesn't exist
Write-Host "[2/8] Creating .gitignore file..." -ForegroundColor Blue
if (-not (Test-Path ".gitignore")) {
    $gitignoreContent = @"
# Python
__pycache__/
*.py[cod]
*`$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual Environment
venv/
env/
ENV/
.venv/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Database
*.db
*.sqlite3

# Temporary files
*.tmp
*.temp
"@
    $gitignoreContent | Out-File -FilePath ".gitignore" -Encoding UTF8
    Write-Host "✅ .gitignore file created" -ForegroundColor Green
} else {
    Write-Host "✅ .gitignore file already exists" -ForegroundColor Green
}

# Add all files
Write-Host "[3/8] Adding all files to Git..." -ForegroundColor Blue
try {
    git add .
    Write-Host "✅ Files added to Git" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to add files to Git" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Commit files
Write-Host "[4/8] Committing files..." -ForegroundColor Blue
$commitMessage = @"
Initial commit: AI-Powered Web Firewall with ML-based threat detection

- Complete AI firewall system with Random Forest classifier
- Real-time threat detection and blocking
- User verification system with progressive challenges
- Comprehensive documentation with screenshots
- Hacker portal for security testing
- Team member profiles and project attribution
- MIT License by Akash Hossain (arknox.in)
- Visual documentation with 15+ screenshots
- Feature extraction for 41 security parameters
- Performance metrics and monitoring capabilities
"@

try {
    git commit -m $commitMessage
    Write-Host "✅ Files committed successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to commit files" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Set main branch
Write-Host "[5/8] Setting main branch..." -ForegroundColor Blue
try {
    git branch -M main
    Write-Host "✅ Main branch set" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to set main branch" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Add remote origin
Write-Host "[6/8] Adding remote origin..." -ForegroundColor Blue
try {
    git remote add origin https://github.com/mdakashhossain1/AI-Powered-Web-Firewall.git
    Write-Host "✅ Remote origin added" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Remote origin might already exist, updating..." -ForegroundColor Yellow
    try {
        git remote set-url origin https://github.com/mdakashhossain1/AI-Powered-Web-Firewall.git
        Write-Host "✅ Remote origin updated" -ForegroundColor Green
    } catch {
        Write-Host "❌ Failed to set remote origin" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Push to GitHub
Write-Host "[7/8] Pushing to GitHub..." -ForegroundColor Blue
Write-Host "NOTE: You may be prompted for GitHub credentials" -ForegroundColor Yellow
try {
    git push -u origin main
    Write-Host "✅ Successfully pushed to GitHub!" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to push to GitHub" -ForegroundColor Red
    Write-Host ""
    Write-Host "Possible solutions:" -ForegroundColor Yellow
    Write-Host "1. Check your internet connection" -ForegroundColor White
    Write-Host "2. Verify GitHub repository exists" -ForegroundColor White
    Write-Host "3. Ensure you have push permissions" -ForegroundColor White
    Write-Host "4. Check if you need to authenticate with GitHub" -ForegroundColor White
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Success message
Write-Host "[8/8] Upload completed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  SUCCESS: Project uploaded to GitHub!" -ForegroundColor Green
Write-Host "  Repository: https://github.com/mdakashhossain1/AI-Powered-Web-Firewall" -ForegroundColor White
Write-Host "  Author: Akash Hossain" -ForegroundColor Yellow
Write-Host "  Website: arknox.in" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Your AI-Powered Web Firewall project is now live on GitHub!" -ForegroundColor Green
Write-Host "The README.md file will display automatically with all screenshots and documentation." -ForegroundColor White
Write-Host ""
Read-Host "Press Enter to exit"
