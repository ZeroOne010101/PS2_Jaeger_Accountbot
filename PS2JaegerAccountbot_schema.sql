--
-- PostgreSQL database dump
--

-- Dumped from database version 11.9 (Raspbian 11.9-0+deb10u1)
-- Dumped by pg_dump version 11.9 (Raspbian 11.9-0+deb10u1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: PS2JaegerAccountbot; Type: DATABASE; Schema: -; Owner: postgres
--

CREATE DATABASE "PS2JaegerAccountbot" WITH TEMPLATE = template0 ENCODING = 'UTF8' LC_COLLATE = 'en_US.UTF-8' LC_CTYPE = 'en_US.UTF-8';


ALTER DATABASE "PS2JaegerAccountbot" OWNER TO postgres;

\connect "PS2JaegerAccountbot"

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: guilds; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.guilds (
    id bigint NOT NULL,
    guild_id bigint NOT NULL,
    utcoffset smallint DEFAULT 0 NOT NULL,
    outfit_name character varying(50) DEFAULT NULL::character varying
);


ALTER TABLE public.guilds OWNER TO postgres;

--
-- Name: guilds_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.guilds_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.guilds_id_seq OWNER TO postgres;

--
-- Name: guilds_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.guilds_id_seq OWNED BY public.guilds.id;


--
-- Name: prefixes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.prefixes (
    fk bigint NOT NULL,
    prefix character varying(15) NOT NULL
);


ALTER TABLE public.prefixes OWNER TO postgres;

--
-- Name: prefixes_fk_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.prefixes_fk_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.prefixes_fk_seq OWNER TO postgres;

--
-- Name: prefixes_fk_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.prefixes_fk_seq OWNED BY public.prefixes.fk;


--
-- Name: sheet_urls; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sheet_urls (
    id bigint NOT NULL,
    fk bigint NOT NULL,
    url character varying(300) NOT NULL
);


ALTER TABLE public.sheet_urls OWNER TO postgres;

--
-- Name: sheet_urls_fk_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.sheet_urls_fk_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.sheet_urls_fk_seq OWNER TO postgres;

--
-- Name: sheet_urls_fk_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.sheet_urls_fk_seq OWNED BY public.sheet_urls.fk;


--
-- Name: sheet_urls_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.sheet_urls_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.sheet_urls_id_seq OWNER TO postgres;

--
-- Name: sheet_urls_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.sheet_urls_id_seq OWNED BY public.sheet_urls.id;


--
-- Name: guilds id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.guilds ALTER COLUMN id SET DEFAULT nextval('public.guilds_id_seq'::regclass);


--
-- Name: prefixes fk; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.prefixes ALTER COLUMN fk SET DEFAULT nextval('public.prefixes_fk_seq'::regclass);


--
-- Name: sheet_urls id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sheet_urls ALTER COLUMN id SET DEFAULT nextval('public.sheet_urls_id_seq'::regclass);


--
-- Name: sheet_urls fk; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sheet_urls ALTER COLUMN fk SET DEFAULT nextval('public.sheet_urls_fk_seq'::regclass);


--
-- Name: guilds guilds_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.guilds
    ADD CONSTRAINT guilds_pkey PRIMARY KEY (id);


--
-- Name: sheet_urls sheet_urls_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sheet_urls
    ADD CONSTRAINT sheet_urls_pkey PRIMARY KEY (id);


--
-- Name: prefixes prefixes_fk_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.prefixes
    ADD CONSTRAINT prefixes_fk_fkey FOREIGN KEY (fk) REFERENCES public.guilds(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: sheet_urls sheet_urls_fk_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sheet_urls
    ADD CONSTRAINT sheet_urls_fk_fkey FOREIGN KEY (fk) REFERENCES public.guilds(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: DATABASE "PS2JaegerAccountbot"; Type: ACL; Schema: -; Owner: postgres
--

GRANT CONNECT ON DATABASE "PS2JaegerAccountbot" TO "PS2JaegerAccountbot";


--
-- Name: TABLE guilds; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.guilds TO "PS2JaegerAccountbot";


--
-- Name: SEQUENCE guilds_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,USAGE ON SEQUENCE public.guilds_id_seq TO "PS2JaegerAccountbot";


--
-- Name: TABLE prefixes; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.prefixes TO "PS2JaegerAccountbot";


--
-- Name: SEQUENCE prefixes_fk_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,USAGE ON SEQUENCE public.prefixes_fk_seq TO "PS2JaegerAccountbot";


--
-- Name: TABLE sheet_urls; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.sheet_urls TO "PS2JaegerAccountbot";


--
-- Name: SEQUENCE sheet_urls_fk_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,USAGE ON SEQUENCE public.sheet_urls_fk_seq TO "PS2JaegerAccountbot";


--
-- Name: SEQUENCE sheet_urls_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,USAGE ON SEQUENCE public.sheet_urls_id_seq TO "PS2JaegerAccountbot";


--
-- Name: DEFAULT PRIVILEGES FOR SEQUENCES; Type: DEFAULT ACL; Schema: -; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres GRANT SELECT,USAGE ON SEQUENCES  TO "PS2JaegerAccountbot";


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: -; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres GRANT SELECT,INSERT,DELETE,UPDATE ON TABLES  TO "PS2JaegerAccountbot";


--
-- PostgreSQL database dump complete
--

