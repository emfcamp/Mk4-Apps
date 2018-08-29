# Rules for apps in the official badge store

See [Rules for apps in the official badge store](https://badge.emfcamp.org/wiki/TiLDA_MK4/Badge_Store_Submissions#Rules_for_apps_in_the_official_badge_store)

# Packaging up your badge app

See [Packaging up your badge app for submission to the store](https://badge.emfcamp.org/wiki/TiLDA_MK4/Badge_Store_Submissions#Packaging_up_your_badge_app_for_submission_to_the_store)

# Using git and GitHub to submit your badge app

Please ensure:

1. You have a [GitHub account](https://github.com/join)  
2. You have [git installed](https://git-scm.com/downloads) on your local computer
3. You have written a badge app [packaged it up](https://badge.emfcamp.org/wiki/TiLDA_MK4/Badge_Store_Submissions#Packaging_up_your_badge_app_for_submission_to_the_store) and [validated](https://badge.emfcamp.org/wiki/TiLDA_MK4/Badge_Store_Submissions#Packaging_up_your_badge_app_for_submission_to_the_store) it

These instructions are tailored around submitting your Badge App but the general principle can be used to raise any pull request.
Please keep pull requests focused on one thing only (like submission of your app), since this makes it easier to merge and test 
in a timely manner.

## Setting up your git username and email address

Using the command line/terminal on your computer type:
```
git config --global user.name “username”  
git config --global user.email  “username@users.noreply.github.com”  
```
Note that the username is the username you use to log into GitHub, not your profile “Name”

## Main flow for contributing

It's important to follow these steps to make changes to your own copy of the emfcamp repo and then raise a pull request that will be merged into the emfcamp repo.

1. Login to GitHub, go to the [emfcamp/Mk4-Apps](https://github.com/emfcamp/Mk4-Apps) repository and click ```Fork``` in 
the top right
2. Using the command line/terminal on your computer type: `git clone <url to YOUR fork>`
3. `cd Mk4-Apps`
4. `git checkout master`
5. `git checkout -b my-app-name` to create a branch with your apps name
6. Copy your app files in their uniquely named folder into the Mk4-Apps/ directory (repo root directory)
7. `git add .` to add all of your app files and directory to your local repo
8. `git commit -m "my-app-name badge app"` note that you can put any message in the quotes
9. `git push origin my-app-name` to update *your* GitHub fork with the change
10. Create pull request using the GitHub UI to merge your changes from your new branch into `emfcamp/Mk4-Apps/master`
11. Repeat from step 4 for new other changes.

The primary thing to remember is that separate pull requests should be created for separate branches.  Never create a pull request from your `master` branch.

Once you have created the pull request, every new commit/push in your branch will propagate from your
fork into the pull reqests in the main github/emfcamp/Mk4-Apps repo.

## Updating your GitHub and local git repo

Later, you can get the changes from the emfcamp/Mk4-Apps repo into your `master` branch by adding emfcamp as a git remote and
merging from it as follows:

1. `git remote add emfcamp https://github.com/emfcamp/Mk4-Apps.git`
2. `git checkout master`
3. `git fetch emfcamp`
4. `git merge emfcamp/master` will update your local repo
5. `git push origin master` will update your fork on GitHub

## Useful links

The GitHub workflow: https://guides.github.com/introduction/flow/index.html

If you need help with pull requests there are guides on GitHub here: https://help.github.com/articles/creating-a-pull-request/
