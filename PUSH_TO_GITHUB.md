# Instructions to Push to GitHub Organization

## Prerequisites

1. You have access to the `memoryful` GitHub organization
2. You have GitHub CLI (`gh`) installed, OR
3. You have SSH keys set up for GitHub

## Option 1: Using GitHub CLI (Recommended)

### Step 1: Authenticate with GitHub
```bash
gh auth login
```

### Step 2: Create Repository in Organization
```bash
cd /Users/sparshnagpal/Desktop/projects/Mem1/evaluation_improved
gh repo create memoryful/mem0-improved --public --source=. --remote=origin --push
```

This will:
- Create a new repository `mem0-improved` in the `memoryful` organization
- Add it as the `origin` remote
- Push all commits to the repository

## Option 2: Manual Setup

### Step 1: Create Repository on GitHub

1. Go to https://github.com/organizations/memoryful/repositories/new
2. Repository name: `mem0-improved`
3. Description: "Improved Mem0 with enhanced memory retrieval, query expansion, and temporal reasoning"
4. Visibility: Public (or Private if preferred)
5. **DO NOT** initialize with README, .gitignore, or license (we already have these)
6. Click "Create repository"

### Step 2: Add Remote and Push

```bash
cd /Users/sparshnagpal/Desktop/projects/Mem1/evaluation_improved

# Add the remote (replace with your GitHub username if using HTTPS)
git remote add origin https://github.com/memoryful/mem0-improved.git

# Or if using SSH:
# git remote add origin git@github.com:memoryful/mem0-improved.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Option 3: Using GitHub Web Interface

1. Create the repository on GitHub (see Step 1 above)
2. Follow the instructions shown after creating the repository:
   ```bash
   cd /Users/sparshnagpal/Desktop/projects/Mem1/evaluation_improved
   git remote add origin https://github.com/memoryful/mem0-improved.git
   git branch -M main
   git push -u origin main
   ```

## Verify Push

After pushing, verify the repository:

1. Visit: https://github.com/memoryful/mem0-improved
2. Check that all files are present
3. Verify README.md is displayed correctly
4. Check that .gitignore is working (no large files committed)

## Next Steps After Pushing

1. **Add repository description and topics** on GitHub:
   - Description: "Improved Mem0 with enhanced memory retrieval, query expansion, temporal reasoning, and graph-based relationships"
   - Topics: `mem0`, `memory`, `rag`, `llm`, `evaluation`, `locomo`, `nlp`, `ai`

2. **Set up GitHub Actions** (optional):
   - Add CI/CD for testing
   - Add automated code quality checks

3. **Create releases** (optional):
   - Tag important commits
   - Create release notes

4. **Enable GitHub Pages** (optional):
   - For documentation hosting

## Troubleshooting

### Issue: Permission Denied
- Ensure you have write access to the `memoryful` organization
- Check your GitHub authentication: `gh auth status`

### Issue: Repository Already Exists
- If repository exists, use: `git remote set-url origin https://github.com/memoryful/mem0-improved.git`
- Then: `git push -u origin main`

### Issue: Large Files
- Check `.gitignore` is working: `git status`
- Remove large files: `git rm --cached <file>`
- Re-commit and push

## Repository URL

After pushing, the repository will be available at:
**https://github.com/memoryful/mem0-improved**

