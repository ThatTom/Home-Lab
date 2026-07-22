# Docker Compose

## Compose Layout and Standards

To aid troubleshooting and diagnostic tasks docker compose files should be constructed in a uniformed manner, using the below guide as reference

``` YAML
 service-name:
    image: prom/prometheus
    ports:
      - 9090:9090
    deploy:
      replicas: 1
      placement:
        constraints:
          - node.label == xyz
          - node.name == xyz
      restart_policy:
        condition: on-failure
```

All images defined should also have a statically set version rather than using :latest to allow for easier version control, updating and pre-release testing

Where possible individual services should be combined into a stack instead of using separate compose files for each

## Update Deployment

1. New version made available for a service that is in service
2. Review updates purpose

- If the update is purely feature based refer to standard release
- If the update is security based/addresses an urgent issue refer to urgent release
- If the update is a development build being used in a non production service then refer to development release

#### Urgent Release

1. Check current version configured within the .env for the service/stack
2. Check new version that is available
3. Update the service/stack .env with the updated version
4. Manually perform a service/stack deployment
5. Verify that the service has been deployed as expected
6. Ensure all other services that depend on the service are also operating as expected

*If services fail to restore, check logs for any clear issues; if not immediately resolvable, change the version back to the previous version and redeploy the stack/service immediately*

#### Standard Release

1. Check current version configured within the .env for the service/stack
2. Check new version that is available
3. Await 1 week post release and check for any reported bugs or issues
4. If no service breaking bugs/issues are found then update the service/stack .env with the updated version
5. Configure the container update procedure with the relevant stack/service and configure the run time to be 2AM of the next morning
6. Following the completion of the procedure verify the service has restored/successfully update the next morning
7. Ensure all other services that depend on the service are also operating as expected

*If services fail to restore, check logs for any clear issues; if not immediately resolvable, change the version back to the previous version and redeploy the stack/service immediately*

#### Development Release

1. Check current version configured within the .env for the service/stack
2. Check new version that is available
3. Update the service/stack .env with the updated version
4. Manually perform a service/stack deployment
5. Verify that the service has been deployed as expected