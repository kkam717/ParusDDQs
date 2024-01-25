# ParusDDQs

Contact: kiankamshad717@gmail.com if you have any questions

# Github instructions

All changes must be specific to a Jira ticket and pushed as a feature upstream of develop branch. Changes should be merged to develop initially through a Pull Request (PR). 

When starting a ticket:

1. `git checkout develop`
2. `git pull`
3. `git checkout -b feature/DT-XXXX-name-of-ticket`

When pushing to github:

1. `git add .`
2. `git commit -m 'useful message'`
3. `git push --set-upstream origin feature/DT-XXXX-name-of-ticket`
4. Go to github and open your branch
5. Create a PR set for merge with develop, and fill in the relevant information
6. Select reviewers if needed