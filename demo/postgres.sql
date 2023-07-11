-- DROP STRUCTURE
DROP TABLE IF EXISTS demo.apikey;
DROP TABLE IF EXISTS demo.outcome;
DROP TABLE IF EXISTS demo.project;
DROP TABLE IF EXISTS demo.client;
DROP SCHEMA IF EXISTS demo;

CREATE SCHEMA demo;

-- CREATE STRUCTURE
CREATE TABLE demo.client (
    client_id       serial      NOT NULL,
    client_name     varchar(200)    NULL,

    CONSTRAINT client_pk PRIMARY KEY (client_id)
);

CREATE TABLE demo.apikey (
    client_id   int             NOT NULL,
    token       varchar(200)    NOT NULL,
    scopes      varchar(200)        NULL,
    CONSTRAINT apikey_client_fk FOREIGN KEY (client_id) REFERENCES demo.client(client_id)
);

CREATE TABLE demo.project (
    project_id      serial      NOT NULL,
    client_id       int         NOT NULL,
    project_name    varchar(200)    NULL,
    deleted         boolean     NOT NULL DEFAULT FALSE,

    CONSTRAINT project_pk PRIMARY KEY (project_id),
    CONSTRAINT project_client_fk FOREIGN KEY (client_id) REFERENCES demo.client(client_id)
);

CREATE TABLE demo.outcome (
    project_id      int             NOT NULL,
    spent           decimal(18,4)   NOT NULL,

    sysmoment       timestamp   NOT NULL DEFAULT NOW(),
    CONSTRAINT report_project_fk FOREIGN KEY (project_id) REFERENCES demo.project(project_id)
);


-- INSERT DEMO DATA
INSERT INTO demo.client (client_name) VALUES
    ('Alpha'),
    ('Beta'),
    ('Gamma'),
    ('Delta');

INSERT INTO demo.apikey (client_id, token, scopes) VALUES
    (1, 'ALPHA_TOKEN', 'common,extra'),
    (4, 'ALPHA_TOKEN', 'common,extra'),
    (2, 'BETA_TOKEN', NULL),
    (3, 'GAMMA_TOKEN', 'common');

INSERT INTO demo.project (client_id, project_name, deleted) VALUES
    (1, 'Alpha_Project_#01', FALSE),    -- #1
    (1, 'Alpha_Project_#02', TRUE),     -- #2
    (1, 'Alpha_Project_#03', FALSE),    -- #3
    (2, 'Beta_Project_#01', TRUE),      -- #4
    (2, 'Beta_Project_#02', TRUE),      -- #5
    (2, 'Beta_Project_#03', FALSE),     -- #6
    (2, 'Beta_Project_#04', FALSE),     -- #7
    (2, 'Beta_Project_#05', FALSE),     -- #8
    (4, 'Delta_Project_#01', FALSE),    -- #9
    (4, 'Delta_Project_#02', FALSE),    -- #10
    (4, 'Delta_Project_#03', TRUE);     -- #11

INSERT INTO demo.outcome (project_id, spent, sysmoment) VALUES
    -- Alpha Project #01
    (1, 62.47, '2007-02-12 07:17:51'),
    (1, 21.318, '2007-02-12 07:19:49'),
    (1, 22.7255, '2007-02-12 07:22:18'),
    (1, 77.5244, '2007-02-12 07:23:39'),
    (1, 13.7089, '2007-02-12 07:26:02'),
    (1, 73.0625, '2007-02-12 07:27:07'),
    (1, 25.3267, '2007-02-12 07:28:49'),
    (1, 46.2587, '2007-02-12 07:29:34'),
    (1, 65.1021, '2007-02-12 07:31:29'),
    (1, 17.8312, '2007-02-12 07:33:53'),
    (1, 84.032, '2007-02-12 07:34:36'),
    (1, 90.3204, '2007-02-12 07:36:55'),
    (1, 29.1086, '2007-02-12 07:38:50'),
    (1, 74.6584, '2007-02-12 07:39:26'),
    (1, 37.1352, '2007-02-12 07:40:33'),
    (1, 38.7745, '2007-02-12 07:41:09'),
    (1, 38.0657, '2007-02-12 07:41:53'),
    (1, 40.6655, '2007-02-12 07:42:22'),
    (1, 75.9146, '2007-02-12 07:42:46'),
    (1, 25.1977, '2007-02-12 07:44:59'),
    (1, 35.2906, '2007-02-12 07:46:13'),
    (1, 94.4622, '2007-02-12 07:47:20'),
    -- Alpha Project #03
    (3, 47.7399, '2007-02-12 12:52:48'),
    (3, 10.4675, '2007-02-12 12:54:44'),
    (3, 73.2481, '2007-02-12 12:56:45'),
    (3, 70.9505, '2007-02-12 12:58:10'),
    (3, 49.3892, '2007-02-12 13:00:17'),
    (3, 32.2919, '2007-02-12 13:01:52'),
    (3, 58.3359, '2007-02-12 13:03:43'),
    (3, 91.3595, '2007-02-12 13:04:04'),
    (3, 96.3534, '2007-02-12 13:05:23'),
    (3, 1.9261, '2007-02-12 13:07:35'),
    (3, 60.62, '2007-02-12 13:08:05'),
    (3, 49.4422, '2007-02-12 13:09:32'),
    (3, 91.6295, '2007-02-12 13:11:46'),
    (3, 40.939, '2007-02-12 13:13:36'),
    (3, 73.5222, '2007-02-12 13:14:00'),
    (3, 96.0444, '2007-02-12 13:15:04'),
    (3, 7.4923, '2007-02-12 13:15:37'),
    (3, 76.6052, '2007-02-12 13:16:04'),
    (3, 82.065, '2007-02-12 13:18:24'),
    -- Delta Project #01
    (9, 99.5503, '2007-02-12 09:23:06'),
    (9, 57.2184, '2007-02-12 09:25:22'),
    (9, 63.6556, '2007-02-12 09:25:47'),
    (9, 20.4563, '2007-02-12 09:27:50'),
    (9, 53.9756, '2007-02-12 09:29:40'),
    (9, 70.5738, '2007-02-12 09:31:27'),
    (9, 25.784, '2007-02-12 09:31:52'),
    (9, 0.4468, '2007-02-12 09:33:12'),
    (9, 24.3482, '2007-02-12 09:33:59'),
    (9, 8.1805, '2007-02-12 09:35:34'),
    (9, 8.6571, '2007-02-12 09:36:32'),
    (9, 20.8394, '2007-02-12 09:37:50');
