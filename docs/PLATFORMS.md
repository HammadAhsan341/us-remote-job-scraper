# US remote scraper — platforms

All boards write to Supabase with `market = us_remote`, same schema as Pakistan/Gulf scrapers.

## Integrated (19 boards)

| Board key        | Website                    | Method                 |
| :--------------- | :------------------------- | :--------------------- |
| `remoteok`       | https://remoteok.com       | JSON API               |
| `remotive`       | https://remotive.com       | JSON API               |
| `weworkremotely` | https://weworkremotely.com | RSS                    |
| `himalayas`      | https://himalayas.app      | JSON API (cursor)      |
| `workingnomads`  | https://workingnomads.com  | JSON API               |
| `jobicy`         | https://jobicy.com         | JSON API (USA filter)  |
| `jobspresso`     | https://jobspresso.co      | RSS (`/jobs/feed/`)    |
| `arbeitnow`      | https://arbeitnow.com      | JSON API (remote only) |
| `dice`           | https://dice.com           | Browser                |
| `builtin`        | https://builtin.com        | Browser                |
| `remote_co`      | https://remote.co          | Browser                |
| `dynamitejobs`   | https://dynamitejobs.com   | Browser                |
| `justremote`     | https://justremote.co      | Browser                |
| `arc`            | https://arc.dev            | Browser                |
| `ziprecruiter`   | https://ziprecruiter.com   | Browser                |
| `monster`        | https://monster.com        | Browser                |
| `careerbuilder`  | https://careerbuilder.com  | Browser                |
| `wellfound`      | https://wellfound.com      | Browser                |
| `indeed`         | https://indeed.com         | Browser (US remote)    |
| `linkedin`       | https://linkedin.com/jobs  | Browser (US remote)    |

## Not integrated (by design)

| Site                   | Reason                                                       |
| :--------------------- | :----------------------------------------------------------- |
| FlexJobs               | Paid membership / login wall                                 |
| Google Jobs            | No stable public feed                                        |
| USAJOBS                | Separate federal API/TOS                                     |
| Greenhouse/Lever/Ashby | Per-company ATS (handled elsewhere in FlowResume import API) |
