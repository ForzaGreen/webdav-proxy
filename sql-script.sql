USE Webdav;

CREATE TABLE `tbl_proxyUsers` (
  `user_id` BIGINT NULL AUTO_INCREMENT,
  `user_username` VARCHAR(45) NULL,
  `user_password` VARCHAR(255) NULL,
  `user_type` ENUM('B','C'),
  `user_server` VARCHAR(200) NULL,
  PRIMARY KEY (`user_id`));

# Sign Up

DELIMITER $$
CREATE DEFINER=`ismail`@`localhost` PROCEDURE `sp_createUser`(
    IN p_username VARCHAR(45),
    IN p_password VARCHAR(255),
    IN p_type ENUM('B','C'),
    IN p_server VARCHAR(200)
)
BEGIN
    if ( select exists (select 1 from tbl_proxyUsers where user_username = p_username) ) THEN
     
        select 'Username Exists !!';
     
    ELSE
     
        insert into tbl_proxyUsers
        (
            user_username,
            user_password,
            user_type,
            user_server
        )
        values
        (
            p_username,
            p_password,
            p_type,
            p_server
        );
     
    END IF;
END$$
DELIMITER ;

# Sign In
DELIMITER $$
CREATE DEFINER=`ismail`@`localhost` PROCEDURE `sp_validateLogin`(
IN p_username VARCHAR(45)
)
BEGIN
    select * from tbl_proxyUsers where user_username = p_username;
END$$
DELIMITER ;

# Secured resources TABLE
CREATE TABLE `tbl_resources` (
  `resource_id` BIGINT NOT NULL AUTO_INCREMENT,
  `resource_path` varchar(200) DEFAULT NULL,
  `resource_uploader` varchar(45) NULL,
  `resource_type` ENUM('file','collection'),
  `resource_key` varchar(255) NULL,
  PRIMARY KEY (`resource_id`)
);

# Add a resource
DELIMITER $$
CREATE DEFINER=`ismail`@`localhost` PROCEDURE `sp_addResource`(
    IN p_path VARCHAR(200),
    IN p_uploader varchar(45),
    IN p_type ENUM('file', 'collection'),
    IN p_key VARCHAR(255)
)
BEGIN
    if ( select exists (select 1 from tbl_resources where resource_path = p_path) ) THEN
     
        select 'Resource Exists !!';
     
    ELSE
     
        insert into tbl_resources
        (
            resource_path,
            resource_uploader,
            resource_type,
            resource_key
        )
        values
        (
            p_path,
            p_uploader,
            p_type,
            p_key
        );
     
    END IF;
END$$
DELIMITER ;

# Give access to the resource
DELIMITER $$
CREATE DEFINER=`ismail`@`localhost` PROCEDURE `sp_accessresource`(
  IN p_path VARCHAR(200)
)
BEGIN
    select * from tbl_resources where resource_path = p_path;
END$$
DELIMITER ;

# Delete a resource
DELIMITER $$
CREATE PROCEDURE `sp_deleteResource` (
  IN p_resourcePath varchar(200)
  )
BEGIN
  delete from tbl_resources where resource_path = p_resourcePath;
END$$
 
DELIMITER ;
