# Use the official Fuseki base image
FROM stain/jena-fuseki


# Set up the necessary environment variables
ENV FUSEKI_HOME=/jena-fuseki
ENV FUSEKI_BASE=/fuseki

# Command to run Fuseki server
CMD ["./fuseki-server", "--file=/fuseki/cso.ttl", "/cso"]
