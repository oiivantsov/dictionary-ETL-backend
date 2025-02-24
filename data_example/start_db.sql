SET client_encoding = 'UTF8';
ALTER SCHEMA public OWNER TO appuser;

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


ALTER TABLE public.finnish_dictionary OWNER TO appuser;

ALTER TABLE public.finnish_dictionary ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.finnish_dictionary_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

-- Instead of COPY, we use INSERT INTO to load data:
INSERT INTO public.finnish_dictionary
  (date_added, date_repeated, level, word, translation, category, category2, source, popularity, repeat_again, comment, example, synonyms, word_formation, frequency)
VALUES
  ('2022-05-09', '2024-12-17', 11, 'laulaa', 'петь', 'Глагол', NULL, NULL, 5, NULL, NULL,
      'v (с)петь, пропеть; {ylistää) вос|певать, -петь; —a jotain! спой что-нибудь!; — bassoäänellä петь басом; — itsensä yleisön sydäмиin покорить публику своим пением; — levylle напеть пластинку; ~ suoraan nuoteista петь с листа; ~ lapsi nukkumaan убаюкать ребёнка',
      NULL, NULL, 1120),
  ('2022-05-09', '2023-06-12', 10, 'yö', 'ночь', 'Существительное', NULL, NULL, 5, NULL,
      'мн.ч. yö - öi', NULL, NULL, NULL, 543),
  ('2022-05-09', '2023-06-07', 10, 'uusi', 'новый', 'Прилагательное', NULL, NULL, 5, NULL,
      NULL, NULL, NULL, NULL, 20),
  ('2022-05-10', '2024-12-25', 11, 'katu', 'улица', 'Существительное', NULL, NULL, 5, NULL, NULL,
      's улица; kaupungin kadut городские }''лицы; huone on kadun puolella комната выходит окнами на улицу, laskea ~a мостить улицу; kuikea kadulla идти по >лице; keskellä ^-a посреди \\лицы <> ajaa jku kadulle выгнать (Г. выбросить) когб-л на улицу; joutua kadulle очутиться на улице',
      NULL, NULL, 905),
  ('2022-05-09', '2024-12-23', 11, 'puhelin', 'телефон', 'Существительное', NULL, NULL, 5, NULL,
      'in - ime // m. imia', 'Pidä puhelin äänettömällä.', NULL, NULL, 1399),
  ('2022-05-09', '2024-12-23', 11, 'tietokone', 'компьютер', 'Существительное', NULL, NULL, 5, NULL,
      'm. eita', NULL, NULL, NULL, 1285),
  ('2022-05-10', '2024-12-21', 11, 'kuu', '1) луна, 2) месяц', 'Существительное', NULL, NULL, 5, NULL, NULL,
      's l) (taivaankappale) луна, месяц; täysi ~ полнолуние; uusi ~ новолуние; vähenevä ~ ущербная луна; -~ paistaa светит луна; ~ meni pilveen луна скрылась за тучами; laskeutuminen ~hun прилунение; odottaa kuin —ta nousevaa ^ ждать как манны небесной 2) (kuukausi) месяц; tämän ~n viidentenä päivänä пятого числа этого месяца; tässä ~ssa в этом месяце О ei ~naan, ei ~na päivänä, ei ~na kullan valkeana kans, runok никогда; ни в жизнь ark',
      NULL, NULL, 1252),
  ('2022-05-10', '2024-12-21', 11, 'kuva', 'картинка', 'Существительное', NULL, NULL, 5, NULL,
      NULL, NULL, NULL, NULL, 196),
  ('2022-11-18', '2024-11-23', 9, 'tunnelma', 'атмосфера, настроение', 'Существительное', NULL, NULL, 5, NULL, NULL,
      '5 (mieliala) настроение, эмоциональный настрой; (ilmapiiri) атмосфера, обстановка; — on korkealla настроение приподнятое; rikkoa ~ испортить настроение; нарушить атмосферу чего-л; kodikas ~ уютная обстановка;',
      'ilmapiiri, mieliala', 'tunne +‎ -lma', 1029),
  ('2023-10-03', '2024-11-27', 9, 'uskotella', '1) убеждать, уверять, 2) воображать, самообольщяться', 'Глагол', NULL, NULL, 4, NULL,
      '1) кого - jklle, часто että-vastike, // vakuutella, yrittää saada uskomaan jtk, 2) кем - ksi // kuvitella, luulotella',
      'Tarvitsetko enemmän aikaa uskotellaksesi, että olet oikeassa\nfrekv. v 1) (vakuutella) уверять|увёрить, за верить, убе|ждать, -дйть кого в чём; — jklle olevansa rehellinen уверять когб-л в своей честности 2) (vakavissaan kuvitella) вообра|жать, -зйть (себя); самообольщаться; —teli olevansa vielä nuori он воображал, что ещё молод; moni ~telee itsensä korvaamattomaksi',NULL, NULL, 6000);


ALTER TABLE ONLY public.finnish_dictionary
    ADD CONSTRAINT finnish_dictionary_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.finnish_dictionary
    ADD CONSTRAINT unique_word_translation UNIQUE (word);

CREATE INDEX idx_level_date ON public.finnish_dictionary USING btree (level, date_repeated);
CREATE INDEX idx_word ON public.finnish_dictionary USING btree (lower(word));