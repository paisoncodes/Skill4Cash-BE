# Skills4Cash-BE

## Description

An Easily Accessible Online Platform Targeted At Local Individual Service Providers, Connecting Them To Potential Customers.

## Project Stack

Python (Django)

## Contribution Guidelines

The following arew the  guidelines for contributing to this project:

1. Fork this repository to get a personal copy on your github account
2. To clone the forked repository to your local machine, open command prompt and run:

```bash
git clone https://github.com/Skill4Cash/Skill4Cash-BE
```

3. Change to the project directory you just cloned

```bash
cd Skill4Cash-BE
```

4. Set Upstream Remote so that changes can be pulled from upstream to your reppository

```bash
git remote add upstream https://github.com/Skill4Cash/Skill4Cash-BE
```

5. Checkout from dev Branch

```bash
git checkout dev
```

6. Checkout Your Feature Branch

Feature Branching Workflow means you create a new branch for every feature or issue you are working on.
It is goood practice for the branch name to reflect the issue being issolved.
So if an issue title is **Update ReadMe.md** then our branch name would be **update-readme**.
create and checkout feature branch by running:

```bash
git checkout -b issue-name
```

7. Setup Development Environment

To setup the development environment to run project run:

```bash
pip install pipenv
pipenv shell
python manage.py migrate

```

8. Set Environment Variables by creating a file called '.env' in the project directory and use the .env.sample to  create a template for
your .env file

9. Run Project by using the following command 'pipenv run python manage.py runserver'


10. After fixing the issue, commit the changes and push them to them to the feature branch of your remote origin

```bash
git add *
git commit -m "descriptive commit message"
git push origin feature-branch-name
```

11. Login to your github account and go to the your forked repository and make a pull request to the *dev* branch
