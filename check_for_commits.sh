#!/usr/bin/env zsh
# src: https://stackoverflow.com/questions/6006759/git-bash-how-to-check-if-theres-a-new-commit-available
# license: CC-BY-SA 5.0
# origin/branch we are interested in
origin="origin"
branch="beta"
# last commit hash
commit=$(git log -n 1 --pretty=format:%H "$origin/$branch")

# url of the remote repo
url=$(git remote get-url "$origin")

for line in "$(git ls-remote -h $url)"; do
    fields=($(echo $line | tr -s ' ' ))
    test "${fields[1]}" == "refs/heads/$branch" || continue
    test "${fields[0]}" == "$commit" && exit  \
        || exit 2
done

exit 500