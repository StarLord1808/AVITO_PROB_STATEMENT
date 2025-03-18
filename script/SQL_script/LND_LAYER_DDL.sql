CREATE TABLE AdsInfo (
    AdID BIGINT PRIMARY KEY,
    LocationID INT,
    CategoryID INT,
    Params TEXT,
    Price FLOAT,
    Title TEXT,
    IsContext BOOLEAN,
    inserted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Category (
    CategoryID INT PRIMARY KEY,
    Level INT,
    ParentCategoryID INT,
    SubcategoryID INT,
    inserted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Location (
    LocationID INT PRIMARY KEY,
    Level INT,
    RegionID INT,
    CityID INT,
    inserted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE PhoneRequestsStream (
    UserID BIGINT,
    IPID BIGINT,
    AdID BIGINT,
    PhoneRequestDate TIMESTAMP,
    inserted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE SearchInfo (
    SearchID BIGINT PRIMARY KEY,
    SearchDate TIMESTAMP,
    IPID BIGINT,
    UserID BIGINT,
    IsUserLoggedOn BOOLEAN,
    SearchQuery TEXT,
    LocationID INT,
    CategoryID INT,
    SearchParams TEXT,
    inserted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE SearchStream (
    ID BIGINT PRIMARY KEY,
    SearchID BIGINT,
    AdID BIGINT,
    Position INT,
    ObjectType INT,
    HistCTR FLOAT,
    inserted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE UserInfo (
    UserID BIGINT PRIMARY KEY,
    UserAgentID INT,
    UserAgentOSID INT,
    UserDeviceID INT,
    UserAgentFamilyID INT,
    inserted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE VisitsStream (
    UserID BIGINT,
    IPID BIGINT,
    AdID BIGINT,
    ViewDate TIMESTAMP,
    inserted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE VisitPhoneRequestStream (
    UserID BIGINT,
    IPID BIGINT,
    AdID BIGINT,
    ViewDate TIMESTAMP,
    PhoneRequestDate TIMESTAMP,
    inserted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE AdsInfo 
ADD CONSTRAINT fk_ads_location FOREIGN KEY (LocationID) REFERENCES Location(LocationID),
ADD CONSTRAINT fk_ads_category FOREIGN KEY (CategoryID) REFERENCES Category(CategoryID);

-- PhoneRequestsStream Foreign Keys
ALTER TABLE PhoneRequestsStream 
ADD CONSTRAINT fk_phone_user_v2 FOREIGN KEY (UserID) REFERENCES UserInfo(UserID),
ADD CONSTRAINT fk_phone_ad_v2 FOREIGN KEY (AdID) REFERENCES AdsInfo(AdID);

-- SearchInfo Foreign Keys
ALTER TABLE SearchInfo 
ADD CONSTRAINT fk_search_user FOREIGN KEY (UserID) REFERENCES UserInfo(UserID),
ADD CONSTRAINT fk_search_location FOREIGN KEY (LocationID) REFERENCES Location(LocationID),
ADD CONSTRAINT fk_search_category FOREIGN KEY (CategoryID) REFERENCES Category(CategoryID);

-- SearchStream Foreign Keys
ALTER TABLE SearchStream 
ADD CONSTRAINT fk_searchstream_search FOREIGN KEY (SearchID) REFERENCES SearchInfo(SearchID),
ADD CONSTRAINT fk_searchstream_ad FOREIGN KEY (AdID) REFERENCES AdsInfo(AdID);

-- VisitsStream Foreign Keys
ALTER TABLE VisitsStream 
ADD CONSTRAINT fk_visits_user FOREIGN KEY (UserID) REFERENCES UserInfo(UserID),
ADD CONSTRAINT fk_visits_ad FOREIGN KEY (AdID) REFERENCES AdsInfo(AdID);

-- VisitPhoneRequestStream Foreign Keys
ALTER TABLE VisitPhoneRequestStream 
ADD CONSTRAINT fk_visitphone_user FOREIGN KEY (UserID) REFERENCES UserInfo(UserID),
ADD CONSTRAINT fk_visitphone_ad FOREIGN KEY (AdID) REFERENCES AdsInfo(AdID);
