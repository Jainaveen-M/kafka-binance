CREATE TABLE `binancetradeorders` (
  `id` bigint(10) NOT NULL AUTO_INCREMENT,
  `clientorderid` int(10) DEFAULT '0',
  `price` varchar(200) NOT NULL DEFAULT '0.00000000',
  `qty` varchar(200) NOT NULL DEFAULT '0.00000000',
  `updatedtime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `createdTime` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `status` smallint(5) unsigned NOT NULL DEFAULT '0',
  `ordertype` smallint(5) unsigned NOT NULL DEFAULT '0',
  `trantype` smallint(5) NOT NULL DEFAULT '0',
  `coinpair` varchar(45) NOT NULL DEFAULT '',
  `exchgid` smallint(5) unsigned NOT NULL DEFAULT '0',
  `exchgorderid` varchar(45) DEFAULT '0',
  `trandata` mediumtext,
  PRIMARY KEY (`id`)
); 


CREATE TABLE `cryptoorder` (
  `id` bigint(10) NOT NULL AUTO_INCREMENT,
  `price` varchar(200) NOT NULL DEFAULT '0.00000000',
  `amount` varchar(200) NOT NULL DEFAULT '0.00000000',
  `status` smallint(5) unsigned NOT NULL DEFAULT '0',
  `ordertype` smallint(5) unsigned NOT NULL DEFAULT '0',
  `trantype` smallint(5) NOT NULL DEFAULT '0',
  `coinpair` varchar(45) NOT NULL DEFAULT '',
  `exchgid` smallint(5) unsigned NOT NULL DEFAULT '0',
  `updatedtime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `createdTime` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
); 






CREATE TABLE `binancetradeorders` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `clientorderid` varchar(200) DEFAULT '0',
  `price` varchar(200) NOT NULL DEFAULT '0.00000000',
  `qty` varchar(200) NOT NULL DEFAULT '0.00000000',
  `updatedtime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `createdTime` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `status` smallint unsigned NOT NULL DEFAULT '0',
  `ordertype` smallint unsigned NOT NULL DEFAULT '0',
  `trantype` smallint NOT NULL DEFAULT '0',
  `coinpair` varchar(45) NOT NULL DEFAULT '',
  `exchgid` smallint unsigned NOT NULL DEFAULT '0',
  `exchgorderid` varchar(45) DEFAULT '0',
  `trandata` mediumtext,
  PRIMARY KEY (`id`)
)

86400000

604800000



CREATE TABLE `binancetradeorders` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `ctid` bigint DEFAULT NULL,
  `clientorderid` varchar(200) DEFAULT '0',
  `price` varchar(200) NOT NULL DEFAULT '0.00000000',
  `qty` varchar(200) NOT NULL DEFAULT '0.00000000',
  `updatedtime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `createdTime` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `status` smallint unsigned NOT NULL DEFAULT '0',
  `action` smallint NOT NULL,
  `ordertype` smallint unsigned NOT NULL DEFAULT '0',
  `trantype` smallint NOT NULL DEFAULT '0',
  `coinpair` varchar(45) NOT NULL DEFAULT '',
  `exchgid` smallint unsigned NOT NULL DEFAULT '0',
  `exchgorderid` varchar(45) DEFAULT '0',
  `trandata` mediumtext,
  PRIMARY KEY (`id`)
)