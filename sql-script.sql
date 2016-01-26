USE Webdav;

CREATE TABLE `tbl_user` (
  `user_id` BIGINT NULL AUTO_INCREMENT,
  `user_username` VARCHAR(45) NULL,
  `user_password` VARCHAR(255) NULL,
  `user_type` ENUM('B','C')
  PRIMARY KEY (`user_id`));

# Sign Uo

DELIMITER $$
CREATE DEFINER=`ismail`@`localhost` PROCEDURE `sp_createUser`(
    IN p_username VARCHAR(45),
    IN p_password VARCHAR(255),
    IN p_type ENUM('B','C')
)
BEGIN
    if ( select exists (select 1 from tbl_user where user_username = p_username) ) THEN
     
        select 'Username Exists !!';
     
    ELSE
     
        insert into tbl_user
        (
            user_username,
            user_password,
            user_type
        )
        values
        (
            p_username,
            p_password,
            p_type
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
    select * from tbl_user where user_username = p_username;
END$$
DELIMITER ;