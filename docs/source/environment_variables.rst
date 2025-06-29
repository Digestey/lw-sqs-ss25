Environment Variables
=====================

This page explains the environment variables used in the application and their purpose.

Application Configuration
-------------------------

- **SECRET_KEY**  
  A secret value used for cryptographic operations such as signing cookies or tokens.  
  Example: ``SECRET_KEY="supersecret"``

- **HOST_IP**  
  IP address where the server should bind. Typically ``0.0.0.0`` to listen on all network interfaces.  
  Example: ``HOST_IP="0.0.0.0"``

Pokémon Quiz Service
--------------------

- **POKEMON_CACHE**  
  Local directory path for caching Pokémon data (e.g., API responses or image files) to reduce redundant API calls.  
  Example: ``POKEMON_CACHE="cache/"``

Database Configuration (MySQL)
------------------------------

- **MYSQL_ROOT_PASSWORD**  
  Root password for the MySQL database server. This is required when initializing the database container.  
  Example: ``MYSQL_ROOT_PASSWORD=pokeballs``

- **MYSQL_DATABASE**  
  Name of the application's primary database.  
  Example: ``MYSQL_DATABASE=pokedb``

- **MYSQL_USER**  
  Custom database user the application uses to access the MySQL database.  
  Example: ``MYSQL_USER=trainer``

- **MYSQL_PASSWORD**  
  Password for the ``MYSQL_USER``.  
  Example: ``MYSQL_PASSWORD=pokeballs``

- **MYSQL_URL**  
  Hostname of the database server used by the application (e.g., in Docker Compose networks).  
  Example: ``MYSQL_URL=pokedb``

Cache Backend (Redis)
---------------------

- **REDIS_HOST**  
  Hostname of the Redis server for caching or background tasks.  
  Example: ``REDIS_HOST=redis``

- **REDIS_PORT**  
  Port Redis is running on. Default is usually ``6379``.  
  Example: ``REDIS_PORT=6379``

Security Notes
--------------

- Never expose secret values (like ``SECRET_KEY`` or ``MYSQL_ROOT_PASSWORD``) in public repositories.
- When deploying in production, consider loading these variables securely from a secrets manager or environment-specific configuration system.
