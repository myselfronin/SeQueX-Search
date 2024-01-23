# Use the official Solr image
FROM solr:8.11-slim

# Copy the script into the container
COPY init-solr.sh /init-solr.sh

# Run the script to create cores
RUN /init-solr.sh