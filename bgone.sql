/*
 Navicat Premium Data Transfer

 Source Server         : 本地
 Source Server Type    : MySQL
 Source Server Version : 50717
 Source Host           : localhost
 Source Database       : bgone

 Target Server Type    : MySQL
 Target Server Version : 50717
 File Encoding         : utf-8

 Date: 04/09/2017 23:18:12 PM
*/

SET NAMES utf8;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
--  Table structure for `follows`
-- ----------------------------
DROP TABLE IF EXISTS `follows`;
CREATE TABLE `follows` (
  `fans_id` int(11) NOT NULL,
  `idol_id` int(11) NOT NULL,
  `timestamp` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`fans_id`,`idol_id`),
  KEY `idol_id` (`idol_id`),
  CONSTRAINT `follows_ibfk_1` FOREIGN KEY (`fans_id`) REFERENCES `users` (`id`),
  CONSTRAINT `follows_ibfk_2` FOREIGN KEY (`idol_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

-- ----------------------------
--  Table structure for `posts`
-- ----------------------------
DROP TABLE IF EXISTS `posts`;
CREATE TABLE `posts` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(64) COLLATE utf8_bin DEFAULT NULL,
  `content` text COLLATE utf8_bin,
  `timestamp` datetime DEFAULT CURRENT_TIMESTAMP,
  `author_id` int(11) DEFAULT NULL,
  `content_html` text COLLATE utf8_bin,
  PRIMARY KEY (`id`),
  KEY `author_id` (`author_id`),
  CONSTRAINT `posts_ibfk_1` FOREIGN KEY (`author_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

-- ----------------------------
--  Table structure for `roles`
-- ----------------------------
DROP TABLE IF EXISTS `roles`;
CREATE TABLE `roles` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(64) DEFAULT NULL,
  `default` tinyint(1) DEFAULT NULL,
  `permit` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `users`
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(64) DEFAULT NULL,
  `role_id` int(11) DEFAULT NULL,
  `email` varchar(64) DEFAULT NULL,
  `password_hash` varchar(128) DEFAULT NULL,
  `confirmed` tinyint(1) DEFAULT NULL,
  `about_me` varchar(64) DEFAULT NULL,
  `last_seen` datetime DEFAULT CURRENT_TIMESTAMP,
  `location` varchar(64) DEFAULT NULL,
  `member_since` datetime DEFAULT CURRENT_TIMESTAMP,
  `name` varchar(64) DEFAULT NULL,
  `avatar_hash` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_users_username` (`username`),
  UNIQUE KEY `ix_users_email` (`email`),
  KEY `role_id` (`role_id`),
  CONSTRAINT `users_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

SET FOREIGN_KEY_CHECKS = 1;
