
CREATE TABLE coopdata (
	nwsli TEXT, 
	date TEXT, 
	time TEXT, 
	`high_F` FLOAT(53), 
	`low_F` FLOAT(53), 
	precip TEXT, 
	snow_inch TEXT, 
	snowd_inch TEXT,
    primary key(nwsli, date),
    foreign key(nwsli) references coopmetadata(id)
);


CREATE TABLE coopmetadata (
	`ID` TEXT, 
	`Station Name` TEXT, 
	`Latitude1` FLOAT(53), 
	`Longitude1` FLOAT(53), 
	`Elevation [m]` FLOAT(53), 
	`Archive Begins` TEXT, 
	`Archive Ends` FLOAT(53), 
	`IEM Network` TEXT, 
	`Attributes` FLOAT(53),
    primary key(`ID`)
);


CREATE TABLE asosdata (
	station TEXT, 
	valid DATETIME, 
	tmpf FLOAT, 
	dwpf FLOAT, 
	relh FLOAT, 
	drct FLOAT, 
	sknt INT, 
	p01i INT, 
	alti FLOAT, 
	mslp TEXT, 
	vsby FLOAT, 
	gust TEXT, 
	skyc1 TEXT, 
	skyc2 TEXT, 
	skyc3 TEXT, 
	skyc4 TEXT, 
	skyl1 TEXT, 
	skyl2 TEXT, 
	skyl3 TEXT, 
	skyl4 TEXT, 
	wxcodes TEXT, 
	ice_accretion_1hr TEXT, 
	ice_accretion_3hr TEXT, 
	ice_accretion_6hr TEXT, 
	peak_wind_gust TEXT, 
	peak_wind_drct TEXT, 
	peak_wind_time TEXT, 
	feel FLOAT, 
	metar TEXT, 
	snowdepth TEXT,
    primary key(station, valid),
    foreign key(station) references asosmetadata(station)
);


CREATE TABLE asosmetadata (
	station TEXT, 
	valid TEXT, 
	lon FLOAT(53), 
	lat FLOAT(53), 
	elevation FLOAT(53),
    primary key(station)
);
