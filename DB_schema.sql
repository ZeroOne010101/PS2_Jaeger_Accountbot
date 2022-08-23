--
-- PostgreSQL database dump
--

-- Dumped from database version 14.5
-- Dumped by pg_dump version 14.5

-- Started on 2022-08-23 16:33:48

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
-- TOC entry 3338 (class 1262 OID 16436)
-- Name: PS2JaegerAccountbot; Type: DATABASE; Schema: -; Owner: postgres
--

CREATE DATABASE "PS2JaegerAccountbot" WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE = 'en_US.UTF-8';


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

SET default_table_access_method = heap;

--
-- TOC entry 209 (class 1259 OID 16437)
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
-- TOC entry 210 (class 1259 OID 16442)
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
-- TOC entry 3341 (class 0 OID 0)
-- Dependencies: 210
-- Name: guilds_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.guilds_id_seq OWNED BY public.guilds.id;


--
-- TOC entry 216 (class 1259 OID 16472)
-- Name: parity_exempt; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.parity_exempt (
    fk bigint NOT NULL,
    user_id bigint NOT NULL
);


ALTER TABLE public.parity_exempt OWNER TO postgres;

--
-- TOC entry 211 (class 1259 OID 16443)
-- Name: prefixes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.prefixes (
    fk bigint NOT NULL,
    prefix character varying(15) NOT NULL
);


ALTER TABLE public.prefixes OWNER TO postgres;

--
-- TOC entry 212 (class 1259 OID 16446)
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
-- TOC entry 3345 (class 0 OID 0)
-- Dependencies: 212
-- Name: prefixes_fk_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.prefixes_fk_seq OWNED BY public.prefixes.fk;


--
-- TOC entry 213 (class 1259 OID 16447)
-- Name: sheet_urls; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sheet_urls (
    id bigint NOT NULL,
    fk bigint NOT NULL,
    url character varying(300) NOT NULL
);


ALTER TABLE public.sheet_urls OWNER TO postgres;

--
-- TOC entry 214 (class 1259 OID 16450)
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
-- TOC entry 3348 (class 0 OID 0)
-- Dependencies: 214
-- Name: sheet_urls_fk_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.sheet_urls_fk_seq OWNED BY public.sheet_urls.fk;


--
-- TOC entry 215 (class 1259 OID 16451)
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
-- TOC entry 3350 (class 0 OID 0)
-- Dependencies: 215
-- Name: sheet_urls_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.sheet_urls_id_seq OWNED BY public.sheet_urls.id;


--
-- TOC entry 3183 (class 2604 OID 16452)
-- Name: guilds id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.guilds ALTER COLUMN id SET DEFAULT nextval('public.guilds_id_seq'::regclass);


--
-- TOC entry 3184 (class 2604 OID 16453)
-- Name: prefixes fk; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.prefixes ALTER COLUMN fk SET DEFAULT nextval('public.prefixes_fk_seq'::regclass);


--
-- TOC entry 3185 (class 2604 OID 16454)
-- Name: sheet_urls id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sheet_urls ALTER COLUMN id SET DEFAULT nextval('public.sheet_urls_id_seq'::regclass);


--
-- TOC entry 3186 (class 2604 OID 16455)
-- Name: sheet_urls fk; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sheet_urls ALTER COLUMN fk SET DEFAULT nextval('public.sheet_urls_fk_seq'::regclass);


--
-- TOC entry 3188 (class 2606 OID 16457)
-- Name: guilds guilds_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.guilds
    ADD CONSTRAINT guilds_pkey PRIMARY KEY (id);


--
-- TOC entry 3190 (class 2606 OID 16459)
-- Name: sheet_urls sheet_urls_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sheet_urls
    ADD CONSTRAINT sheet_urls_pkey PRIMARY KEY (id);


--
-- TOC entry 3193 (class 2606 OID 16480)
-- Name: parity_exempt parity_exempt_fk_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.parity_exempt
    ADD CONSTRAINT parity_exempt_fk_fkey FOREIGN KEY (fk) REFERENCES public.guilds(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- TOC entry 3191 (class 2606 OID 16460)
-- Name: prefixes prefixes_fk_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.prefixes
    ADD CONSTRAINT prefixes_fk_fkey FOREIGN KEY (fk) REFERENCES public.guilds(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- TOC entry 3192 (class 2606 OID 16465)
-- Name: sheet_urls sheet_urls_fk_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sheet_urls
    ADD CONSTRAINT sheet_urls_fk_fkey FOREIGN KEY (fk) REFERENCES public.guilds(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- TOC entry 3339 (class 0 OID 0)
-- Dependencies: 3338
-- Name: DATABASE "PS2JaegerAccountbot"; Type: ACL; Schema: -; Owner: postgres
--

GRANT CONNECT ON DATABASE "PS2JaegerAccountbot" TO "PS2JaegerAccountbot";


--
-- TOC entry 3340 (class 0 OID 0)
-- Dependencies: 209
-- Name: TABLE guilds; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.guilds TO "PS2JaegerAccountbot";


--
-- TOC entry 3342 (class 0 OID 0)
-- Dependencies: 210
-- Name: SEQUENCE guilds_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,USAGE ON SEQUENCE public.guilds_id_seq TO "PS2JaegerAccountbot";


--
-- TOC entry 3343 (class 0 OID 0)
-- Dependencies: 216
-- Name: TABLE parity_exempt; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.parity_exempt TO "PS2JaegerAccountbot";


--
-- TOC entry 3344 (class 0 OID 0)
-- Dependencies: 211
-- Name: TABLE prefixes; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.prefixes TO "PS2JaegerAccountbot";


--
-- TOC entry 3346 (class 0 OID 0)
-- Dependencies: 212
-- Name: SEQUENCE prefixes_fk_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,USAGE ON SEQUENCE public.prefixes_fk_seq TO "PS2JaegerAccountbot";


--
-- TOC entry 3347 (class 0 OID 0)
-- Dependencies: 213
-- Name: TABLE sheet_urls; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.sheet_urls TO "PS2JaegerAccountbot";


--
-- TOC entry 3349 (class 0 OID 0)
-- Dependencies: 214
-- Name: SEQUENCE sheet_urls_fk_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,USAGE ON SEQUENCE public.sheet_urls_fk_seq TO "PS2JaegerAccountbot";


--
-- TOC entry 3351 (class 0 OID 0)
-- Dependencies: 215
-- Name: SEQUENCE sheet_urls_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,USAGE ON SEQUENCE public.sheet_urls_id_seq TO "PS2JaegerAccountbot";


--
-- TOC entry 2040 (class 826 OID 16470)
-- Name: DEFAULT PRIVILEGES FOR SEQUENCES; Type: DEFAULT ACL; Schema: -; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres GRANT SELECT,USAGE ON SEQUENCES  TO "PS2JaegerAccountbot";


--
-- TOC entry 2041 (class 826 OID 16471)
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: -; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres GRANT SELECT,INSERT,DELETE,UPDATE ON TABLES  TO "PS2JaegerAccountbot";


-- Completed on 2022-08-23 16:33:48

--
-- PostgreSQL database dump complete
--

