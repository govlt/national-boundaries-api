# National Boundaries and Addresses API of Lithuania

Access comprehensive data on national boundaries and addresses registered in the Republic of Lithuania. This API
provides detailed information and geometries about counties, municipalities, elderships, residential areas, streets,
addresses, and rooms.

## Key features

1. **No extra dependencies**: A single Docker image without the need for databases like Postgres or MySQL.
2. **Easy Usage**: OpenAPI support for quick client and contract generation in your favorite programming language.
3. **Advanced Filtering and Searching**: Filter by geometries, various attributes, transform geometries to different
   SRIDs, and more.
4. **Frequent Updates**: Daily Docker image updates on changes to boundaries or addresses.

5. **Infinite horizontal scaling**: API can be scaled horizontally without state or extra services.
6. **Compact and Efficient**: SQLite database with all boundaries, addresses, and geometries under 500 MB.
7. **Flexible Deployment**: Easily deployable on various infrastructures, supporting containerization and orchestration
   tools.
8. **Completely Open Source and Free**: Join our community of contributors and users. The entire project is open-source
   and free of restrictions..

## Self-hosting

Host National Boundaries and Addresses API of Lithuania on your own infrastructure.

### Docker Image

Here's an example of its usage with Docker Compose:

```yaml
services:
  national-boundaries-api:
    image: ghcr.io/govlt/national-boundaries-api:main
    pull_policy: always
    restart: unless-stopped
    ports:
      - "80:80"
    healthcheck:
      test: [ "CMD-SHELL", "wget --no-verbose --tries=1 --spider http://127.0.0.1:80/health || exit 1" ]
      interval: 5s
      timeout: 3s
      start_period: 5s
      retries: 5
```

Additional docker image environment options:

| Environment Variable | Description                                                                                                                                                                                                                                                                  | Default Value |
|----------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------|
| `SENTRY_DSN`         | The DSN for Sentry, used for error tracking and monitoring. Leave empty if Sentry is not used.                                                                                                                                                                               |               |
| `SENTRY_ENVIRONMENT` | Specifies the environment for Sentry (e.g., production, staging, development).                                                                                                                                                                                               | `production`  |
| `ROOT_URL`           | The root URL of the application. Only change if the application is mounted below a specific URL path.                                                                                                                                                                        |               |
| `WORKERS`            | The number of Uvicorn worker processes to run. Adjust based on workload and available resources. If you have a cluster of machines with Kubernetes, Docker Swarm, or another similar system, handle replication at the cluster level and keep a single worker per container. | `1`           |

### SQLite Database

Optionally, use the SQLite database with all boundaries and addresses directly without running the
national-boundaries-api. Download the latest database version [here](TODO).

## Getting Started Development

To embark on your development journey, follow these simple steps:

- **Install Python 3.12+:** [Download Python](https://www.python.org/downloads/)
- **Install Poetry 1.8+:** [Download Poetry](https://python-poetry.org/docs/#installation)
- **Install SpatialLite 5+**: [Download SpatialLite](https://www.gaia-gis.it/fossil/libspatialite/index)
- **Install GDAL 3.9+:** [Download GDAL](https://gdal.org/download.html) (Needed only for building the SQLite file on
  your computer)

After setting up a Python virtual environment and installing dependencies with Poetry, create the database by
executing `create-database.sh`.

To run the development API, execute the following command (change SPATIALITE_LIBRARY_PATH to the path of SpatialLite on
your computer):

```shell
SPATIALITE_LIBRARY_PATH="mod_spatialite.dylib" python -m uvicorn src.main:app --reload
```

## License

This project is licensed under the [MIT License](./LICENSE). Data from this API is licensed
under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.lt). For more information,
visit [Registrų centras](https://www.registrucentras.lt/p/1187).

While preparing the National Boundaries and Addresses API, some changes were made such as changing attribute names to
English. For full details, check out the [create-database.sh](./create-database.sh) file.

## Contributing

Join our community! Your contributions are invaluable. Whether you spot issues or have innovative ideas, feel free to
open an issue or submit a pull request. Check out
our [contribution guidelines](https://github.com/govlt/.github/blob/main/CONTRIBUTING.md) for more details.