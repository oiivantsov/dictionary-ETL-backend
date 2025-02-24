
-- created by using pg_dump from original db

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

ALTER SCHEMA public OWNER TO appuser;

SET default_tablespace = '';

SET default_table_access_method = heap;

CREATE TABLE public.finnish_dictionary (
    id bigint NOT NULL,
    date_added date,
    date_repeated date,
    level integer,
    word text,
    translation text,
    category text,
    category2 text,
    source text,
    popularity integer,
    repeat_again integer,
    comment text,
    example text,
    synonyms text,
    word_formation text,
    frequency integer,
    CONSTRAINT level_min_max CHECK (((level >= 0) AND (level <= 12))),
    CONSTRAINT popularity_min_max CHECK (((popularity >= 0) AND (popularity <= 5)))
);


ALTER TABLE public.finnish_dictionary OWNER TO oleg;

ALTER TABLE public.finnish_dictionary ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.finnish_dictionary_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

COPY public.finnish_dictionary (id, date_added, date_repeated, level, word, translation, category, category2, source, popularity, repeat_again, comment, example, synonyms, word_formation, frequency) FROM stdin;
1	2022-05-09	2024-12-17	11	laulaa	петь	Глагол	\N	\N	5	\N	\N	v (с)петь, пропеть; {ylistää) вос|певать, -петь; —a jotain! спой что-нибудь!; — bassoäänellä петь басом; — itsensä yleisön sydämiin покорить публику своим пением; — levylle напеть пластинку; ~ suoraan nuoteista петь с листа; ~ lapsi nukkumaan убаюкать ребёнка; — ava {soinnukas) певучий, мелодичный О ~ ylistystä jklle петь дифирамбы кому-л 	\N	\N	1120
2	2022-05-09	2023-06-12	10	yö	ночь	Существительное	\N	\N	5	\N	мн.ч. yö - öi	\N	\N	\N	543
3	2022-05-09	2023-06-07	10	uusi	новый	Прилагательное	\N	\N	5	\N	\N	\N	\N	\N	20
5	2022-05-10	2024-12-25	11	katu	улица	Существительное	\N	\N	5	\N	\N	s улица; kaupungin kadut городские }'лицы; huone on kadun puolella комната выходит окнами на улицу, laskea ~a мостить улицу; kuikea kadulla идти по >лице; keskellä ^-a посреди \\лицы <> ajaa jku kadulle выгнать (Г. выбросить) когб-л на улицу; joutua kadulle очутиться на улице 	\N	\N	905
6	2022-05-09	2024-12-23	11	puhelin	телефон	Существительное	\N	\N	5	\N	in - ime // m. imia	Pidä puhelin äänettömällä.	\N	\N	1399
7	2022-05-09	2024-12-23	11	tietokone	компьютер	Существительное	\N	\N	5	\N	m. eita	\N	\N	\N	1285
8	2022-05-10	2024-12-21	11	kuu	1) луна, 2) месяц	Существительное	\N	\N	5	\N	\N	s l) (taivaankappale) луна, месяц; täysi ~ полнолуние; uusi ~ новолуние; vähenevä ~ ущербная луна; -~ paistaa светит луна; ~ meni pilveen луна скрылась за тучами; laskeutuminen ~hun прилунение; odottaa kuin —ta nousevaa ^ ждать как манны небесной 2) (kuukausi) месяц; tämän ~n viidentenä päivänä пятого числа этого месяца; tässä ~ssa в этом месяце О ei ~naan, ei ~na päivänä, ei ~na kullan valkeana kans, runok никогда; ни в жизнь ark 	\N	\N	1252
9   2022-05-10	2024-12-21	11	kuva	картинка	Существительное	\N	\N	5	\N	\N	\N	\N	\N	196
10	2022-11-18	2024-11-23	9	tunnelma	атмосфера, настроение	Существительное	\N	\N	5	\N	\N	5 (mieliala) настроение, эмоциональный настрой; (ilmapiiri) атмосфера, обстановка; — on korkealla настроение приподнятое; rikkoa ~ испортить настроение; нарушить атмосферу чего-л; kodikas ~ уютная обстановка; 	ilmapiiri, mieliala	tunne +‎ -lma	1029
11	2023-10-03	2024-11-27	9	uskotella	1) убеждать, уверять, 2) воображать, самообольщяться	Глагол	\N	\N	4	\N	1) кого - jklle, часто että-vastike, // vakuutella, yrittää saada uskomaan jtk, 2) кем - ksi // kuvitella, luulotella	Tarvitsetko enemmän aikaa uskotellaksesi, että olet oikeassa\nfrekv. v 1) (vakuutella) уверять|увёрить, за верить] за верить, убе|ждать, -дйть кого в чём; — jklle olevansa rehellinen уверять когб-л в своей честности 2) (vakavissaan kuvitella) вообра|жать, -зйть (себя); самообольщаться; —teli olevansa vielä nuori он воображал, что ещё молод; moni ~telee itsensä korvaamattomaksi многие считают себя незаменимыми 	vakuutella, kuvitella	\N	\N
\.


--
-- Name: finnish_dictionary finnish_dictionary_pkey; Type: CONSTRAINT; Schema: public; Owner: appuser
--

ALTER TABLE ONLY public.finnish_dictionary
    ADD CONSTRAINT finnish_dictionary_pkey PRIMARY KEY (id);


--
-- Name: finnish_dictionary unique_word_translation; Type: CONSTRAINT; Schema: public; Owner: appuser
--

ALTER TABLE ONLY public.finnish_dictionary
    ADD CONSTRAINT unique_word_translation UNIQUE (word);


--
-- Name: idx_level_date; Type: INDEX; Schema: public; Owner: appuser
--

CREATE INDEX idx_level_date ON public.finnish_dictionary USING btree (level, date_repeated);


--
-- Name: idx_word; Type: INDEX; Schema: public; Owner: appuser
--

CREATE INDEX idx_word ON public.finnish_dictionary USING btree (lower(word));


--
-- Name: DEFAULT PRIVILEGES FOR SEQUENCES; Type: DEFAULT ACL; Schema: -; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres GRANT ALL ON SEQUENCES TO appuser;


--
-- Name: DEFAULT PRIVILEGES FOR TYPES; Type: DEFAULT ACL; Schema: -; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres GRANT ALL ON TYPES TO appuser;


--
-- Name: DEFAULT PRIVILEGES FOR FUNCTIONS; Type: DEFAULT ACL; Schema: -; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres GRANT ALL ON FUNCTIONS TO appuser;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: -; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres GRANT ALL ON TABLES TO appuser;


--
-- PostgreSQL database dump complete
--
