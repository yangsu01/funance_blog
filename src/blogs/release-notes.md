### v1.1.2 (14-05-2024)

- Added filtering options for leaderboard plots
- Updated daily plots to show % growth instead of portfolio value
- Updated calculations from 2 decimal places to 4... (Thanks _piyewe74_)
- Fixed bug where user was unable to join game
- Fixed bug where user was unable to create games with no transaction fees
- Fixed line plot x axis units displayed
  <br> <br>

### v1.1.1 (10-05-2024)

- Removed login requirement to view certain pages
- Added search, sort, and filter options to games list
- Updated backend validation (thanks _stockmaster_ and _woriy96668_)
  <br> <br>

### v1.1.0 (02-05-2024)

- Added blog catalog and blog posts
- Added about page
- Fixed incorrect time display
- Fixed issue where stocks were unable to be bought if initial search had whitespace
- Fixed transaction fee displayed incorrectly for Flat Fees
  <br> <br>

### v1.0.0 (02-05-2024)

- 1.0 Release!!! after 1.5 months!!!
- Updated frontend to use React
- Completely reworked UI
- Added game lobbies with custom rules
- Many quality of life and efficiency changes...
  <br> <br>

### v0.4.1 (14-03-2024)

- Updated `blogs` route to `blog`
- Updated button colors in auth layouts
- updated create portfolio UI
  <br> <br>

### v0.4.0 (14-03-2024)

- Added dynamic navigation bar and optimized for mobile layouts
- Updated button colors and text to be consistent between layouts
- Fixed navigation buttons breaking upon url route changes
- Fixed issue where users are not able to sell shares they own
  <br> <br>

#### v0.3.0 (13-03-2024)

- Added Blogs
  - Added `Blog` table in database
  - converts markdown to html for rendering
- Updated page layouts
  - Stardardized fonts and text size
  - Standardized page margins and layouts
- Removed redundant Bootstrap classes from html
- Updated file names to be consistant
  <br> <br>

#### v0.2.1 (12-03-2024)

- Updated time series plots on Leaderboard and Dashboard
  - Removed large time gaps between datapoints when markets are closed
- Fixed Dashboard pie charts text clipping
- Fixed Dashboard portfolio growth (%) calculations
  <br> <br>

#### v0.2.0 (11-03-2024)

- Added Sector and Holdings breakdown charts to Dashboard
- Added `sector` and `industry` columns to `Holdings` table in database
- Fixed displayed timezones
- Updated backend file structure
- Removed unused dependencies from code
  <br> <br>

#### v0.1.3 (10-03-2024)

- Fixed UI display on mobile
- Fixed ticker search function
  <br> <br>

#### v0.1.2 (9-03-2024)

- Fixed issue where password was unable to be saved when creating an account
  <br> <br>

#### v0.1.1 (9-03-2024)

- Fixed issue where database was wiped everytime a new deployment was made
  <br> <br>

#### v0.1.0 (9-03-2024)

- Initial Pilot Test
- Added basic stock portfolio simulation game
- Added real time stock data lookup
