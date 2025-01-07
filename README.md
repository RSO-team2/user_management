# User Management

## Purpose and API Documentation

[Postman API Documentation](https://documenter.getpostman.com/view/26454602/2sAYBbd8zB)

The API serves as the dedicated microservice for interaction with users database. For more information regarding the users database, please refer to the following repository: [Database Setup](https://github.com/RSO-team2/database_setup)

### Use-Cases

1. Add a new user into the database.
2. Login user by checking the password.
3. Retrieve users' additional information.
3. > **Others Not Yet Implemented** 

## Developer Setup

In order to develop and run this use-case, you have to do the following:
- Install Git, Python and Pip on your machine
- Clone this repository
- Install the required Python packages using the following command: `pip install -r requirements.txt`
- A Digital Ocean account
- A Postgres Managed Database on Digital Ocean (add it's URL to your local .env file under the key DATABASE_URL).
- For a basic understanding of the deployment process please refer to the following documentation of Digital Ocean:
    - [Build and Deploy Your First Image to Your First Cluster](https://docs.digitalocean.com/products/kubernetes/getting-started/deploy-image-to-cluster/)
    - [Set up CI/CD using GitHub Actions](https://docs.digitalocean.com/products/container-registry/how-to/enable-push-to-deploy/)
- When you have completed the steps above, the API will be deployed to your Digital Ocean account when you commit any changes and you can start using it.
- Configur

## Checklist

Service Completion Checklist
  - [ ] Documentation (specific documentation)
    - [ ] Inputs and outputs
    - [ ] Types management
  - [x] READMEs (general documentation)
    - [x] Purpose
    - [ ] Use-cases
  - [x] CI/CD Pipeline
  - [x] Cloud deployment

