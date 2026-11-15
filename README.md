# Git Collaboration Practice Repository

A small, disposable repository for practicing Git commands. Each numbered folder is a guided exercise. Do the commands in order from this directory; commands that edit files should be followed by `git status` so you can see what changed.

## Start here

```bash
cd ~/Desktop/Capstone_Project
git status
git log --oneline --all
```

This folder is its own Git repository. It is intentionally separate from your existing capstone project.

## 1. Working tree, staging, and commits

1. Inspect `01-basics/notes.md` and `01-basics/todo.txt`.
2. Edit `01-basics/notes.md`, adding a sentence.
3. Run `git status` and `git diff`.
4. Stage only that file: `git add 01-basics/notes.md`.
5. Inspect the staged change: `git diff --staged`.
6. Commit it: `git commit -m "Add a practice note"`.
7. Edit `todo.txt`, stage and commit it separately.
8. Review history with `git log --oneline`.

## 2. Branches and pull-request simulation

1. Create a branch: `git switch -c feature/add-greeting`.
2. Edit `02-branching/greeting.txt`, then stage and commit it.
3. Compare your branch with main: `git diff main...HEAD`.
4. Return to main: `git switch main`.
5. Merge the branch: `git merge --no-ff feature/add-greeting`.
6. Inspect the result with `git log --oneline --graph --decorate --all`.

This local merge simulates the branch-and-review part of a pull request. For an actual hosted pull request, push a branch to a remote and open a PR on the hosting site.

## 3. Make and resolve a conflict

1. On `main`, change the first line of `03-conflicts/message.txt` to `Message from main` and commit it.
2. Create a branch: `git switch -c feature/change-message`.
3. Change that same first line to `Message from feature` and commit it.
4. Return to main and make a different change to that same line, then commit.
5. Merge the feature branch: `git merge feature/change-message`.
6. Git will report a conflict. Open the file, choose the final text, and remove the `<<<<<<<`, `=======`, and `>>>>>>>` marker lines.
7. Run `git status`, stage the resolved file, and finish with `git commit`.

To abandon this practice conflict and return to the pre-merge state, use `git merge --abort` while the merge is in progress.

## 4. Hygiene and undo practice

1. Read `04-hygiene/.gitignore` and confirm `04-hygiene/scratch.tmp` is ignored with `git status --ignored --short`.
2. Make a change to `04-hygiene/checklist.md`, inspect it using `git diff`, then discard only that unstaged change with `git restore 04-hygiene/checklist.md`.
3. Stage a small change and unstage it with `git restore --staged <path>`; the file edit remains in your working tree.
4. Learn what a commit changes with `git show --stat --oneline HEAD`.

Avoid `git reset --hard`, `git clean -fd`, and force-push while learning. They can discard work or rewrite shared history.

## Push to a remote (optional)

Only connect this practice repo to the intended practice repository on GitHub. Do not add the remote for your existing capstone application unless you want these exercises published there too.

After creating an empty GitHub repository for these exercises, copy its URL and run:

```bash
git remote add origin <your-practice-repository-url>
git remote -v
git push -u origin main
```

For a feature branch, use `git push -u origin feature/add-greeting`. Pushing publishes commits to the configured remote. Review `git remote -v` before pushing.

## Restarting the practice

Keep the commits and repeat the exercises on new branches. To start over from scratch, first make sure there is nothing here you need, then remove this practice folder's `.git` directory and initialize it again. Do not run cleanup commands from your home directory.
