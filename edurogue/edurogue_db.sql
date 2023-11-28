-- phpMyAdmin SQL Dump
-- version 5.1.1deb4
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Oct 08, 2021 at 09:29 AM
-- Server version: 10.5.12-MariaDB-1
-- PHP Version: 7.4.21

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `edurogue`
--

-- --------------------------------------------------------

--
-- status meaning in device table
-- 0 - Device good configured (GOODY)
-- 1 - Device bad configured (BADLY)
-- 2 - Probably GOODY
-- 3 -
-- 4 - BADLY but un-noticed (not logged because network problems)
-- 5 - GOODY but un-noticed (not logged because network problems)

--
-- Table structure for table `devices`
--

CREATE TABLE `devices` (
  `timestamp` timestamp NOT NULL DEFAULT current_timestamp(),
  `device` varchar(17) NOT NULL,
  `user` varchar(50) DEFAULT NULL,
  `status` tinyint(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Table structure for table `log`
--

CREATE TABLE `log` (
  `timestamp` timestamp NOT NULL DEFAULT current_timestamp(),
  `device` varchar(17) NOT NULL,
  `user` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Table structure for table `temp`
--

CREATE TABLE `temp` (
  `timestamp` timestamp NOT NULL DEFAULT current_timestamp(),
  `device` varchar(17) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `devices`
--
ALTER TABLE `devices`
  ADD PRIMARY KEY (`device`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

-- User privileges

--GRANT USAGE ON *.* TO `edurogue`@`localhost` IDENTIFIED BY PASSWORD '*9B4178A30BDCED9DAD84D2041520A57A2337A0C3';
--GRANT ALL PRIVILEGES ON `edurogue`.* TO `edurogue`@`localhost`;