## LEXI Online File Storage Structure

link to the NASA (CDAweb) data: https://cdaweb.gsfc.nasa.gov/pub/data/

Potential link to the LEXI data: https://cdaweb.gsfc.nasa.gov/pub/data/lexi/

# Directory Structure on the web server

```
.
├── README.md
├── documents
├── ephemeris
    ├── lexi_ephm_YYYYMMDD_v0.0.0.cdf
├── images
├── payload_data
    ├── l1
        ├── lexi_l1_mcp_YYYYMMDD_v0.0.0.cdf
    ├── l2
        ├── lexi_l2_mcp_YYYYMMDD_hhmmss_hhmmss_ss_v0.0.0.fits
├── updates.html
└── release_notes.html
├── webpages
    ├── index.html
    ├── updates.html
    └── release_notes.html
```

This a brief description of the directory structure on the web server.
## descriptions

-- The 'documents' directory contains any supporting documents we might want to include on the
website.

-- The 'ephemeris' directory contains the ephemeris files for the LEXI spacecraft. These files most
likely will be in SPICE format. Or may be in a cdf format. The naming convention for the ephemeris
files is: lexi_ephm_YYYYMMDD_v0.0.0.cdf.

-- The 'images' directory contains any images we might want to include on the website.

-- The 'payload_data' directory contains the payload data. The payload data is organized by level.
The level 1 data is in the 'l1' directory and the level 2 data is in the 'l2' directory. level 1 data
will have the following parameters: time, RA (right ascension), and DEC (declination). The naming
convention for the level 1 data is: lexi_l1_mcp_YYYYMMDD_v0.0.0.cdf.
The level 2 data will be the integrated images using the level 1 data. It will be provided in a fits
format and will have the following naming convention:
lexi_l2_mcp_YYYYMMDD_hhmmss_hhmmss_ss_v0.0.0.fits. where the first hhmmss is the start time of the
image and the second hhmmss is the end time of the image. The ss is the integration time of the image
in seconds.
-- The 'updates.html' file is a file that contains the updates to the data.
-- The 'release_notes.html' file is a file that contains the release notes for the data.
-- The 'webpages' directory contains the webpages for the website, currently it is hosted at the
following link: https://lexi-bu.github.io/
