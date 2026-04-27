--
-- PostgreSQL database dump
--

\restrict UwqYXSGT1cyPQH9Yc1UqFmJMF4F4ObfeytJb3qAsw08TN4URDGcui2WuOs3QzvF

-- Dumped from database version 18.3
-- Dumped by pg_dump version 18.3

-- Started on 2026-04-27 14:18:29

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
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
-- TOC entry 226 (class 1259 OID 16436)
-- Name: conversations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.conversations (
    id integer NOT NULL,
    user_id character varying(100),
    user_message text,
    bot_response text,
    detected_intent character varying(50),
    confidence numeric(5,4),
    user_feedback character varying(10),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.conversations OWNER TO postgres;

--
-- TOC entry 225 (class 1259 OID 16435)
-- Name: conversations_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.conversations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.conversations_id_seq OWNER TO postgres;

--
-- TOC entry 5017 (class 0 OID 0)
-- Dependencies: 225
-- Name: conversations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.conversations_id_seq OWNED BY public.conversations.id;


--
-- TOC entry 222 (class 1259 OID 16406)
-- Name: delivery_zones; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.delivery_zones (
    id integer NOT NULL,
    key_name character varying(100) NOT NULL,
    name character varying(200) NOT NULL,
    base_price integer NOT NULL,
    coefficient numeric(5,2) DEFAULT 1.0,
    note text
);


ALTER TABLE public.delivery_zones OWNER TO postgres;

--
-- TOC entry 221 (class 1259 OID 16405)
-- Name: delivery_zones_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.delivery_zones_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.delivery_zones_id_seq OWNER TO postgres;

--
-- TOC entry 5018 (class 0 OID 0)
-- Dependencies: 221
-- Name: delivery_zones_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.delivery_zones_id_seq OWNED BY public.delivery_zones.id;


--
-- TOC entry 220 (class 1259 OID 16390)
-- Name: materials; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.materials (
    id integer NOT NULL,
    key_name character varying(100) NOT NULL,
    name character varying(200) NOT NULL,
    price_per_ton numeric(10,2),
    price_per_bag numeric(10,2),
    bag_weight integer,
    unit character varying(50) NOT NULL,
    description text,
    type character varying(20) DEFAULT 'ton'::character varying
);


ALTER TABLE public.materials OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 16389)
-- Name: materials_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.materials_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.materials_id_seq OWNER TO postgres;

--
-- TOC entry 5019 (class 0 OID 0)
-- Dependencies: 219
-- Name: materials_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.materials_id_seq OWNED BY public.materials.id;


--
-- TOC entry 224 (class 1259 OID 16422)
-- Name: microdistricts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.microdistricts (
    id integer NOT NULL,
    zone_id integer,
    name character varying(200) NOT NULL,
    slang_name character varying(200)
);


ALTER TABLE public.microdistricts OWNER TO postgres;

--
-- TOC entry 223 (class 1259 OID 16421)
-- Name: microdistricts_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.microdistricts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.microdistricts_id_seq OWNER TO postgres;

--
-- TOC entry 5020 (class 0 OID 0)
-- Dependencies: 223
-- Name: microdistricts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.microdistricts_id_seq OWNED BY public.microdistricts.id;


--
-- TOC entry 228 (class 1259 OID 16447)
-- Name: training_examples; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.training_examples (
    id integer NOT NULL,
    text text NOT NULL,
    intent character varying(50) NOT NULL,
    source character varying(50) DEFAULT 'manual'::character varying,
    approved boolean DEFAULT false,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.training_examples OWNER TO postgres;

--
-- TOC entry 227 (class 1259 OID 16446)
-- Name: training_examples_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.training_examples_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.training_examples_id_seq OWNER TO postgres;

--
-- TOC entry 5021 (class 0 OID 0)
-- Dependencies: 227
-- Name: training_examples_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.training_examples_id_seq OWNED BY public.training_examples.id;


--
-- TOC entry 4834 (class 2604 OID 16439)
-- Name: conversations id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.conversations ALTER COLUMN id SET DEFAULT nextval('public.conversations_id_seq'::regclass);


--
-- TOC entry 4831 (class 2604 OID 16409)
-- Name: delivery_zones id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.delivery_zones ALTER COLUMN id SET DEFAULT nextval('public.delivery_zones_id_seq'::regclass);


--
-- TOC entry 4829 (class 2604 OID 16393)
-- Name: materials id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.materials ALTER COLUMN id SET DEFAULT nextval('public.materials_id_seq'::regclass);


--
-- TOC entry 4833 (class 2604 OID 16425)
-- Name: microdistricts id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.microdistricts ALTER COLUMN id SET DEFAULT nextval('public.microdistricts_id_seq'::regclass);


--
-- TOC entry 4836 (class 2604 OID 16450)
-- Name: training_examples id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.training_examples ALTER COLUMN id SET DEFAULT nextval('public.training_examples_id_seq'::regclass);


--
-- TOC entry 5009 (class 0 OID 16436)
-- Dependencies: 226
-- Data for Name: conversations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.conversations (id, user_id, user_message, bot_response, detected_intent, confidence, user_feedback, created_at) FROM stdin;
\.


--
-- TOC entry 5005 (class 0 OID 16406)
-- Dependencies: 222
-- Data for Name: delivery_zones; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.delivery_zones (id, key_name, name, base_price, coefficient, note) FROM stdin;
6	советский	Советский район	4000	1.15	\N
7	железнодорожный	Железнодорожный район	5000	1.43	\N
5	октябрьский	Октябрьский район	3500	1.00	\N
\.


--
-- TOC entry 5003 (class 0 OID 16390)
-- Dependencies: 220
-- Data for Name: materials; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.materials (id, key_name, name, price_per_ton, price_per_bag, bag_weight, unit, description, type) FROM stdin;
10	щебень	Щебень	1700.00	\N	\N	тонна	Для бетона, фундамента, дорожек	ton
11	щебень_5_20	Щебень фракции 5-20мм	1700.00	\N	\N	тонна	Мелкий щебень для бетона и дорожек	ton
12	щебень_20_40	Щебень фракции 20-40мм	1650.00	\N	\N	тонна	Средний щебень для фундамента	ton
13	песок	Песок строительный	800.00	\N	\N	тонна	Для бетона и строительных работ	ton
14	гравий	Гравий	1600.00	\N	\N	тонна	Для дренажа и строительства	ton
15	крошка	Крошка гранитная	1800.00	\N	\N	тонна	Для огорода, бетона, стяжки	ton
16	отсев	Отсев речной	900.00	\N	\N	тонна	Для бетона, стяжки, штукатурки	ton
17	доломит	Доломит (белый камень)	\N	350.00	45	мешок	Для сада, дорожек, декора	bag
18	мраморный_щебень	Мраморный щебень в мешках	\N	350.00	45	мешок	Для сада, огорода, дорожек и декора	bag
\.


--
-- TOC entry 5007 (class 0 OID 16422)
-- Dependencies: 224
-- Data for Name: microdistricts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.microdistricts (id, zone_id, name, slang_name) FROM stdin;
22	7	Аршан	Аршан
23	7	Верхняя Берёзовка	Берёзовка
24	7	Восточный	Восточный
25	7	Загорск	Авиазавод
26	7	Загорск	Машзавод
27	7	Зеленхоз	Зеленхоз
28	7	Зеленый	Зеленый
29	7	КиРЗ	Кирзавод
30	7	Лысая гора	Лысая гора
31	7	Матросова	Матросова
32	7	Мостовой	Мостовой
33	7	Орешково	Орешково
34	7	ПВЗ	ПВЗ
35	7	Площадка	Площадка
36	7	Солнечный	Солнечный
37	7	Шишковка	Шишковка
38	7	Шишковка	3-й цинхай
39	5	Комушка	Комушка
40	5	Новая Комушка	Новая Комушка
41	5	Забайкальский	Забайкальский
42	5	Горького	пос. Горького
43	5	Звездный	Звездный
44	5	Зерногородок	Зерногородок
45	5	Импульс	Импульс
46	5	Медведчиково	Медведчиково
47	5	Мелькомбинат	Мелькомбинат
48	5	Мясокомбинат	Мясокомбинат
49	5	Николаевский	Николаевский
50	5	Октябрьский	Октябрь
51	5	Октябрьский	Зауда
52	5	Радуга	Радуга
53	5	Светлый	Светлый
54	5	Силикатный	Силикатный
55	5	Сокольники	Сокольники
56	5	Сосновый Бор	Сосновка
57	5	Степной	Степной
58	5	Таежный	Таежный
59	5	Тальцы	Тальцы
60	5	Тепловик	Тепловик
61	5	Тулунжа	Тулунжа
62	5	Энергетик	Энергетик
63	5	Южный	Южный
64	5	18-19 кварталы	5-й цинхай
65	5	20-й квартал	Форт
66	5	20-й квартал	NST
67	5	20-й квартал	Новостройка
68	5	43-й квартал	Поле чудес
69	5	43-й квартал	Заря
70	5	47-й квартал	Манхэттен
71	5	47-й квартал	Чанкайши
72	5	102-й квартал	Загробная
73	5	Нахаловка	Нахаловка
74	6	Вагжанова	Вагжанова
75	6	Исток	Исток
76	6	Сокол	Сокол
77	6	Солдатский	Солдатский
78	6	Сосновый Бор	Сосновка
79	6	Степной	Степной
80	6	Аэропорт	Аэропорт
81	6	Заречный	Заречка
82	6	Тапхар	Тапхар
83	6	Левый берег	Левый берег
84	6	Кумыска	Кумыска
85	6	Стеклозавод	Стеклозавод
86	6	Центр	Центр
87	6	Центр	Арбат
88	6	Площадь Советов	Башка
89	6	Площадь Советов	Голова
90	6	Площадь Революции	Палец
91	6	Площадь Революции	Бигфак
92	6	Площадь Банзарова	Банзарка
93	6	ул. Борсоева	Китайка
94	6	ул. Приречная	Радарка
95	6	ул. Бабушкина	Новянка
96	6	ул. Геологическая	Шестидом
97	6	ул. Профсоюзная	1-й цинхай
98	6	ул. Профсоюзная	Дворянское гнездо
99	6	ул. Модогоева	Лесная моль
100	6	Проспект 50-летия Октября	BroadWay
101	6	Проспект 50-летия Октября	0-й цинхай
102	6	Проспект Победы	Злодейка
103	6	Проспект Победы	Аквариум
104	6	Филармония	Шары
105	6	Филармония	Яйца
106	6	Кооперативный техникум	Копчик
107	6	ТСК	Суконка
108	6	Элеватор	Элеватор
109	6	Элеватор	0-й цинхай
110	6	Ресбольница	Бруски
111	6	Пентагон	Пентагон
112	6	Пентагон	4-й цинхай
113	6	Городской сад	Горсад
114	6	Городской сад	Огород
115	6	Батарейка	Батарейка
116	6	Почтовка	Почтовка
117	6	Гортоп	Гортоп
118	6	Дружба	Дружба
119	6	Казахстан	Казахстан
120	6	Вертолетка	Вертолетка
121	6	Старая барахолка	Старая барахолка
\.


--
-- TOC entry 5011 (class 0 OID 16447)
-- Dependencies: 228
-- Data for Name: training_examples; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.training_examples (id, text, intent, source, approved, created_at) FROM stdin;
\.


--
-- TOC entry 5022 (class 0 OID 0)
-- Dependencies: 225
-- Name: conversations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.conversations_id_seq', 1, false);


--
-- TOC entry 5023 (class 0 OID 0)
-- Dependencies: 221
-- Name: delivery_zones_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.delivery_zones_id_seq', 8, true);


--
-- TOC entry 5024 (class 0 OID 0)
-- Dependencies: 219
-- Name: materials_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.materials_id_seq', 25, true);


--
-- TOC entry 5025 (class 0 OID 0)
-- Dependencies: 223
-- Name: microdistricts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.microdistricts_id_seq', 126, true);


--
-- TOC entry 5026 (class 0 OID 0)
-- Dependencies: 227
-- Name: training_examples_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.training_examples_id_seq', 1, false);


--
-- TOC entry 4851 (class 2606 OID 16445)
-- Name: conversations conversations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.conversations
    ADD CONSTRAINT conversations_pkey PRIMARY KEY (id);


--
-- TOC entry 4845 (class 2606 OID 16420)
-- Name: delivery_zones delivery_zones_key_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.delivery_zones
    ADD CONSTRAINT delivery_zones_key_name_key UNIQUE (key_name);


--
-- TOC entry 4847 (class 2606 OID 16418)
-- Name: delivery_zones delivery_zones_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.delivery_zones
    ADD CONSTRAINT delivery_zones_pkey PRIMARY KEY (id);


--
-- TOC entry 4841 (class 2606 OID 16404)
-- Name: materials materials_key_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.materials
    ADD CONSTRAINT materials_key_name_key UNIQUE (key_name);


--
-- TOC entry 4843 (class 2606 OID 16402)
-- Name: materials materials_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.materials
    ADD CONSTRAINT materials_pkey PRIMARY KEY (id);


--
-- TOC entry 4849 (class 2606 OID 16429)
-- Name: microdistricts microdistricts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.microdistricts
    ADD CONSTRAINT microdistricts_pkey PRIMARY KEY (id);


--
-- TOC entry 4853 (class 2606 OID 16460)
-- Name: training_examples training_examples_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.training_examples
    ADD CONSTRAINT training_examples_pkey PRIMARY KEY (id);


--
-- TOC entry 4854 (class 2606 OID 16473)
-- Name: microdistricts microdistricts_zone_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.microdistricts
    ADD CONSTRAINT microdistricts_zone_id_fkey FOREIGN KEY (zone_id) REFERENCES public.delivery_zones(id) ON DELETE CASCADE;


-- Completed on 2026-04-27 14:18:30

--
-- PostgreSQL database dump complete
--

\unrestrict UwqYXSGT1cyPQH9Yc1UqFmJMF4F4ObfeytJb3qAsw08TN4URDGcui2WuOs3QzvF

