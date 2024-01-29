# SeQueX Search

SeQueX Search is a sophisticated retrieval system designed for Computer Science publications, enhancing the search process through Semantic Query Expansion (SQE) techniques. Integrating Named Entity Disambiguation and leveraging the CSO Ontology for query expansion, significantly improves the accuracy and relevance of search results.

## Features

- **Publication Search:** Users can input queries to retrieve relevant publications, with the system analyzing the context and returning paginated results.
- **Comparison of Retrieval Methods:** The platform enables users to compare results from traditional keyword-based searches with those enhanced by SQE, illustrating the benefits of the latter.
- **Log Insights:** The system provides transparency into the SQE process by allowing users to view logs directly in the browser, offering insights into the underlying mechanisms.

## Getting Started with Docker

This section provides a comprehensive guide to setting up and running SeQueX Search using Docker, ideal for development and testing environments.

### Prerequisites

Before proceeding, ensure that Docker and Docker Compose are installed and running on your system.

### Running the Application

1. **Clone the Repository:**
   Clone the SeQueX Search repository to your local machine using the following command:
   ```
   git clone https://gitlab.hrz.tu-chemnitz.de/vsr/edu/advising/ma-rabinson-ghatani.git
   ```

2. **Navigate to the Project Directory:**
   Change into the project directory with:
   ```
   cd ma-rabinson-ghatani
   ```

3. **Configure Environment Variable:**
   Before building and running the docker containers, you need to configure the environment variables:
   - Copy the docker/.env.example file to docker/.env.
   - Update the ports that are available if any conflicts otherwise leave the default PORTs used

   Same for flask app (Modify if necessary)
   - Copy the flaskapp/env.example file to flaskapp/.env.

4. **Build Docker Containers:**
   Within the `/docker` directory, build the Docker containers using:
   ```
   docker-compose build
   ```
5. **Download CSO NER Model:**
   This model is required in CSONER service for entity recognition
   ```
   docker exec -it flaskapp flask download:cso_ner_model
   ```
5. **Start the Application:**
   Launch the application in detached mode by running:
   ```
   docker-compose up -d
   ```

### Preparing the Database

Before the application is fully operational, you need to set up and optionally populate the database:

1. **Migrate the Database:**
   Perform database migrations to set up the necessary tables and schemas:
   ```
   docker exec -it flaskapp flask db upgrade
   ```

2. **(Option 1)For data: Load Database Dump:**
   If you wish to start with a pre-populated database, load the dump after completing the migration step. Unzip the docker/dump.sql and then import it to the database
   ```
   docker exec -i postgres_db psql -U admin -d thesis < docker/dump.sql
   
3. **(Option 2) For data: Run commands**
   - Access the flaskapp bash
     ```bash
     docker exec -i flaskapp bash
     ```
   - Within the Docker container, run the following Flask commands to pull papers from AIDA and store CSO topics in database:
     ```bash
     flask aida:pull_cs_papers
     flask aida:pull_paper_topics
     flask topic:add_from_cso
     flask topic:get_dbpedia_link
     flask topic:get_description_from_dbpedia
     ```

### Indexing Data in Solr Core

With the application and database ready, proceed to index the data:

1. **Index CSO Topics:**
   ```
   docker exec -it flaskapp flask solr:index_cso_topics
   ```

2. **Index Papers:**
   ```
   docker exec -it flaskapp flask solr:index_papers
   ```

3. **For Evaluation Purposes:**
   To index evaluation papers, use:
   ```
   docker exec -it flaskapp flask solr:index_evaluation_papers
   ```

### Accessing SeQueX Search
Access the Fuseki UI at `http://localhost:<APP_HOST_PORT>/`, replacing `<APP_HOST_PORT>` with the port configured in your Docker setup.

### Accessing Fuseki Server

For querying CSO from the Fuseki UI, follow these steps:

1. Credentials can be found in the `shiro.ini` file. Navigate to the Fuseki directory and view the credentials:
   ```
   cd /path/to/fuseki
   cat shiro.ini
   ```
2. Access the Fuseki UI at `http://localhost:<FUSEKI_SERVER_PORT>/`, replacing `<FUSEKI_SERVER_PORT>` with the port configured in your Docker setup.

## Authors

- **Rabinson Ghatani** - *Initial work* - [YourUsername](https://github.com/myselfronin)