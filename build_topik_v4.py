"""
build_topik_v4.py
TOPIK 1~6급 전체 앱 생성 (B2 구조)
- 기존 16개 큐레이션 카테고리 유지
- 1-2급 잔여 단어 → 9개 토픽 카테고리
- 3-6급 → 레벨별 (명사 / 동사형용사 / 기타) 3그룹씩
"""
import json, re, sys, io
from pathlib import Path
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

BASE = Path(r"C:\Users\jayki\Desktop\Preply Korean")
VDIR = BASE / "topik_vocab"

# ── 데이터 로드 ────────────────────────────────────────────────────────────────
clean    = json.loads((VDIR / "topik_vocab_clean.json").read_text(encoding="utf-8"))
meanings = json.loads((VDIR / "_translate_progress.json").read_text(encoding="utf-8"))
cache_ex    = json.loads((VDIR / "_cache_example.json").read_text(encoding="utf-8"))
cache_ex_en = json.loads((VDIR / "_cache_example_en.json").read_text(encoding="utf-8"))
all_words = clean["all"]

# ── 다중품사 키 처리 ───────────────────────────────────────────────────────────
word_cnt   = Counter(w["word"] for w in all_words)
multi_pos  = {w for w, c in word_cnt.items() if c > 1}

def ex_key(w):
    return f"{w['word']}|{w['pos_en']}" if w["word"] in multi_pos else w["word"]

# ── 단어별 데이터 조회 함수 ──────────────────────────────────────────────────
MANUAL_MEANINGS = {
    "개|bound noun": "counter (for objects); piece; unit",
    "개|noun":       "dog",
    "가지|bound noun":"kind; sort; type",
    "가지|noun":     "branch; twig; eggplant",
    "각|adjective":  "each; every",
    "각|noun":       "angle",
    "간|noun":       "liver; seasoning",
    "간|affix":      "between; for (duration)",
    "간|bound noun": "between; among",
    "구|numeral":    "nine (9)",
    "구|noun":       "ward; district; phrase",
    "말|noun":       "speech; word; language",
    "말|bound noun": "end; close (of a period)",
    "배|noun":       "stomach; ship; pear",
    "배":            "stomach; ship; pear",
    "눈|noun":       "eye; snow",
    "눈":            "eye; snow",
    "다리|noun":     "leg; bridge",
    "다리":          "leg; bridge",
    "자|noun":       "ruler (measuring tool)",
    "자|interjection":"well; now; come on",
    "자|affix":      "-ist; -er (person suffix)",
    "권|bound noun": "volume; copy (counter for books)",
    "권|affix":      "right; privilege",
    "가요|noun":     "K-pop; Korean popular music",
    "가요":          "K-pop; Korean popular music",
    "발|noun":       "foot; feet",
    "발|affix":      "bound; departing from",
    "손|noun":       "hand",
    "동|noun":       "east; same; district",
    "식|noun":       "meal; ceremony",
    "문|noun":       "door; gate; writing",
    "반|noun":       "half; class; group",
    "나|pronoun":    "I; me (casual)",
    "일|noun":       "work; day; matter",
    "일|numeral":    "one (1); number one",
}
MANUAL_EXAMPLES = {
    "계시다":        ("어머니가 한국에 계셔요.",      "My mother is in Korea."),
    "주무시다":      ("할머니가 낮잠을 주무셔요.",    "My grandmother is taking a nap."),
    "드시다":        ("할아버지가 밥을 드셔요.",      "My grandfather is eating."),
    "누나":          ("누나한테 전화해요.",           "I call my older sister."),
    "간|bound noun": ("서울과 부산 간을 이동해요.",   "I travel between Seoul and Busan."),
}

def word_data(w):
    """단어 dict → (meaning_en, ex_ko, ex_en)"""
    key  = ex_key(w)
    bare = w["word"]
    mkey = key if "|" in key else bare
    meaning = (MANUAL_MEANINGS.get(mkey)
                or MANUAL_MEANINGS.get(bare)
                or meanings.get(bare, bare))
    if key in MANUAL_EXAMPLES or bare in MANUAL_EXAMPLES:
        ex_ko, ex_en = MANUAL_EXAMPLES.get(key) or MANUAL_EXAMPLES.get(bare)
    else:
        ex_ko = cache_ex.get(key, cache_ex.get(bare, w.get("example", "")))
        ex_en = cache_ex_en.get(key, cache_ex_en.get(bare, ""))
    return meaning, ex_ko, ex_en

# ─────────────────────────────────────────────────────────────────────────────
# 기존 16개 카테고리 (원본 유지)
# ─────────────────────────────────────────────────────────────────────────────
EXISTING_DATA = [
{"id":1,"ko":"🙏 인사 표현","en":"Greetings & Expressions","color":"#6366f1","short":"인사","lv_min":1,"lv_max":2,"words":[
{"no":1,"k":"안녕하세요","e":"hello / hi","s":"안녕하세요! 처음 뵙겠습니다.","lv":1},
{"no":2,"k":"안녕","e":"hi / bye","s":"친구한테 안녕! 하고 인사했어요.","lv":1},
{"no":3,"k":"안녕히 가세요","e":"goodbye (to someone leaving)","s":"선생님, 안녕히 가세요!","lv":1},
{"no":4,"k":"안녕히 계세요","e":"goodbye (to someone staying)","s":"저 먼저 가요. 안녕히 계세요.","lv":1},
{"no":5,"k":"감사합니다","e":"thank you (formal)","s":"도와주셔서 감사합니다.","lv":1},
{"no":6,"k":"고마워요","e":"thank you (polite)","s":"친구야, 고마워요!","lv":1},
{"no":7,"k":"죄송합니다","e":"I'm sorry (formal)","s":"늦어서 정말 죄송합니다.","lv":1},
{"no":8,"k":"미안해요","e":"sorry (polite)","s":"기다리게 해서 미안해요.","lv":1},
{"no":9,"k":"괜찮아요","e":"it's okay / no problem","s":"괜찮아요, 걱정하지 마세요.","lv":1},
{"no":10,"k":"네","e":"yes (polite)","s":"네, 알겠습니다.","lv":1},
{"no":11,"k":"아니요","e":"no (polite)","s":"아니요, 괜찮습니다.","lv":1},
{"no":12,"k":"맞아요","e":"that's right / correct","s":"네, 맞아요!","lv":1},
{"no":13,"k":"저기요","e":"excuse me","s":"저기요, 잠깐만요.","lv":1},
{"no":14,"k":"잠깐만요","e":"just a moment","s":"잠깐만요, 전화 받을게요.","lv":1},
{"no":15,"k":"잠시만요","e":"one moment please","s":"잠시만요, 곧 올게요.","lv":1},
{"no":16,"k":"반갑습니다","e":"nice to meet you","s":"처음 뵙겠습니다. 반갑습니다!","lv":1},
{"no":17,"k":"처음 뵙겠습니다","e":"nice to meet you (first time)","s":"처음 뵙겠습니다. 저는 민준이에요.","lv":2},
{"no":18,"k":"존댓말","e":"respectful speech style","s":"선생님께는 존댓말을 써요.","lv":2},
{"no":19,"k":"어서 오세요","e":"welcome","s":"어서 오세요! 무엇을 드릴까요?","lv":2},
{"no":20,"k":"실례합니다","e":"excuse me (formal)","s":"실례합니다, 길 좀 물어볼게요.","lv":2},
{"no":21,"k":"고마워","e":"thanks (casual)","s":"도와줘서 고마워!","lv":1},
{"no":22,"k":"미안해","e":"sorry (casual)","s":"늦어서 미안해.","lv":1},
{"no":23,"k":"응","e":"yeah / yep (casual)","s":"응, 알았어!","lv":1},
{"no":24,"k":"아니","e":"nope (casual)","s":"아니, 그게 아니야.","lv":1},
{"no":25,"k":"괜찮아","e":"it's okay (casual)","s":"걱정 마, 괜찮아.","lv":1},
]},
{"id":2,"ko":"🎒 기본 명사","en":"Basic Nouns & Pronouns","color":"#8b5cf6","short":"명사","lv_min":1,"lv_max":2,"words":[
{"no":1,"k":"저","e":"I / me (polite)","s":"저는 학생이에요.","lv":1},
{"no":2,"k":"나","e":"I / me (casual)","s":"나는 학교에 가요.","lv":1},
{"no":3,"k":"이거","e":"this (thing)","s":"이거 얼마예요?","lv":1},
{"no":4,"k":"이것","e":"this","s":"이것은 제 가방이에요.","lv":1},
{"no":5,"k":"그것","e":"that (near other person)","s":"그것은 뭐예요?","lv":1},
{"no":6,"k":"저것","e":"that (far away)","s":"저것은 학교예요.","lv":1},
{"no":7,"k":"뭐","e":"what","s":"이거 뭐예요?","lv":1},
{"no":8,"k":"가방","e":"bag","s":"가방이 무거워요.","lv":1},
{"no":9,"k":"책","e":"book","s":"책을 읽어요.","lv":1},
{"no":10,"k":"사전","e":"dictionary","s":"사전에서 단어를 찾아요.","lv":1},
{"no":11,"k":"핸드폰","e":"cell phone","s":"핸드폰이 없어요.","lv":1},
{"no":12,"k":"카메라","e":"camera","s":"카메라로 사진을 찍어요.","lv":1},
{"no":13,"k":"물","e":"water","s":"물을 마셔요.","lv":1},
{"no":14,"k":"사과","e":"apple","s":"사과가 맛있어요.","lv":1},
{"no":15,"k":"우유","e":"milk","s":"아침에 우유를 마셔요.","lv":1},
{"no":16,"k":"학교","e":"school","s":"학교에 가요.","lv":1},
{"no":17,"k":"사무실","e":"office","s":"사무실에서 일해요.","lv":1},
{"no":18,"k":"집","e":"house / home","s":"집에 있어요.","lv":1},
{"no":19,"k":"친구","e":"friend","s":"친구를 만나요.","lv":1},
{"no":20,"k":"학생","e":"student","s":"저는 학생이에요.","lv":1},
{"no":21,"k":"선생님","e":"teacher","s":"선생님이 친절해요.","lv":1},
{"no":22,"k":"고양이","e":"cat","s":"고양이가 귀여워요.","lv":1},
{"no":23,"k":"모자","e":"hat / cap","s":"모자를 써요.","lv":1},
{"no":24,"k":"이 사람","e":"this person","s":"이 사람은 누구예요?","lv":2},
{"no":25,"k":"그 사람","e":"that person","s":"그 사람이 제 친구예요.","lv":2},
{"no":26,"k":"있다","e":"to exist / to have","s":"돈이 있어요.","lv":1},
{"no":27,"k":"없다","e":"to not exist / to not have","s":"시간이 없어요.","lv":1},
{"no":28,"k":"아니에요","e":"it's not / no","s":"아니에요, 제가 아니에요.","lv":1},
]},
{"id":3,"ko":"🍜 음식 & 맛","en":"Food & Taste","color":"#ec4899","short":"음식","lv_min":1,"lv_max":2,"words":[
{"no":1,"k":"밥","e":"rice / meal","s":"밥을 먹어요.","lv":1},
{"no":2,"k":"김밥","e":"gimbap (seaweed rice roll)","s":"김밥이 맛있어요.","lv":1},
{"no":3,"k":"김치","e":"kimchi","s":"김치가 매워요.","lv":1},
{"no":4,"k":"삼겹살","e":"grilled pork belly","s":"삼겹살을 구워 먹어요.","lv":1},
{"no":5,"k":"치킨","e":"fried chicken","s":"치킨 먹고 싶어요.","lv":1},
{"no":6,"k":"피자","e":"pizza","s":"피자를 주문했어요.","lv":1},
{"no":7,"k":"햄버거","e":"hamburger","s":"햄버거 하나 주세요.","lv":1},
{"no":8,"k":"아이스크림","e":"ice cream","s":"더울 때 아이스크림을 먹어요.","lv":1},
{"no":9,"k":"케이크","e":"cake","s":"생일 케이크예요.","lv":1},
{"no":10,"k":"커피","e":"coffee","s":"커피 한 잔 주세요.","lv":1},
{"no":11,"k":"오렌지","e":"orange","s":"오렌지 주스 마실래요?","lv":1},
{"no":12,"k":"사탕","e":"candy","s":"사탕이 달아요.","lv":1},
{"no":13,"k":"맛있다","e":"delicious / tasty","s":"이 음식이 정말 맛있어요!","lv":1},
{"no":14,"k":"맛없다","e":"not tasty","s":"이거 맛없어요.","lv":1},
{"no":15,"k":"맵다","e":"spicy","s":"김치가 너무 매워요.","lv":2},
{"no":16,"k":"달다","e":"sweet","s":"이 케이크가 달아요.","lv":2},
{"no":17,"k":"배고프다","e":"to be hungry","s":"배고파요, 뭐 먹을까요?","lv":1},
{"no":18,"k":"김치찌개","e":"kimchi stew","s":"김치찌개를 끓여요.","lv":2},
{"no":19,"k":"냉면","e":"cold noodles","s":"여름에 냉면을 먹어요.","lv":1},
{"no":20,"k":"된장찌개","e":"soybean paste stew","s":"된장찌개가 구수해요.","lv":2},
]},
{"id":4,"ko":"🏃 동사 기초","en":"Basic Action Verbs","color":"#f59e0b","short":"동사①","lv_min":1,"lv_max":2,"words":[
{"no":1,"k":"가다","e":"to go","s":"학교에 가요.","lv":1},
{"no":2,"k":"오다","e":"to come","s":"친구가 와요.","lv":1},
{"no":3,"k":"먹다","e":"to eat","s":"밥을 먹어요.","lv":1},
{"no":4,"k":"마시다","e":"to drink","s":"물을 마셔요.","lv":1},
{"no":5,"k":"보다","e":"to see / watch","s":"영화를 봐요.","lv":1},
{"no":6,"k":"읽다","e":"to read","s":"책을 읽어요.","lv":1},
{"no":7,"k":"쓰다","e":"to write / use","s":"편지를 써요.","lv":1},
{"no":8,"k":"사다","e":"to buy","s":"옷을 사요.","lv":1},
{"no":9,"k":"자다","e":"to sleep","s":"일찍 자요.","lv":1},
{"no":10,"k":"일어나다","e":"to wake up / get up","s":"아침에 일찍 일어나요.","lv":1},
{"no":11,"k":"하다","e":"to do","s":"공부를 해요.","lv":1},
{"no":12,"k":"만들다","e":"to make","s":"케이크를 만들어요.","lv":2},
{"no":13,"k":"놀다","e":"to play / hang out","s":"친구들이랑 놀아요.","lv":1},
{"no":14,"k":"웃다","e":"to laugh / smile","s":"재미있어서 웃어요.","lv":1},
{"no":15,"k":"기다리다","e":"to wait","s":"버스를 기다려요.","lv":1},
{"no":16,"k":"전화하다","e":"to phone / call","s":"친구한테 전화해요.","lv":1},
{"no":17,"k":"일하다","e":"to work","s":"회사에서 일해요.","lv":1},
{"no":18,"k":"공부하다","e":"to study","s":"한국어를 공부해요.","lv":1},
{"no":19,"k":"청소하다","e":"to clean","s":"방을 청소해요.","lv":1},
{"no":20,"k":"요리하다","e":"to cook","s":"저녁을 요리해요.","lv":1},
{"no":21,"k":"노래하다","e":"to sing","s":"노래방에서 노래해요.","lv":1},
{"no":22,"k":"도착하다","e":"to arrive","s":"역에 도착했어요.","lv":2},
{"no":23,"k":"버리다","e":"to throw away","s":"쓰레기를 버려요.","lv":2},
{"no":24,"k":"팔다","e":"to sell","s":"과일을 팔아요.","lv":2},
{"no":25,"k":"찾다","e":"to look for / find","s":"화장실을 찾아요.","lv":1},
]},
{"id":5,"ko":"🔢 숫자 & 단위","en":"Numbers & Counters","color":"#10b981","short":"숫자","lv_min":1,"lv_max":2,"words":[
{"no":1,"k":"일","e":"1 (sino-Korean)","s":"일 번이 뭐예요?","lv":1},
{"no":2,"k":"이","e":"2 (sino-Korean)","s":"이월은 짧아요.","lv":1},
{"no":3,"k":"삼","e":"3 (sino-Korean)","s":"삼 더하기 이는 오예요.","lv":1},
{"no":4,"k":"사","e":"4 (sino-Korean)","s":"사람이 사 명이에요.","lv":1},
{"no":5,"k":"오","e":"5 (sino-Korean)","s":"오 분 있어요.","lv":1},
{"no":6,"k":"육","e":"6 (sino-Korean)","s":"육 층이에요.","lv":1},
{"no":7,"k":"칠","e":"7 (sino-Korean)","s":"칠월 칠 일이에요.","lv":1},
{"no":8,"k":"팔","e":"8 (sino-Korean)","s":"팔 원이에요.","lv":1},
{"no":9,"k":"구","e":"9 (sino-Korean)","s":"구 월이에요.","lv":1},
{"no":10,"k":"십","e":"10 (sino-Korean)","s":"십 분 후에 와요.","lv":1},
{"no":11,"k":"백","e":"100","s":"백 원짜리예요.","lv":1},
{"no":12,"k":"천","e":"1,000","s":"천 원이에요.","lv":1},
{"no":13,"k":"만","e":"10,000","s":"만 원짜리 지폐예요.","lv":2},
{"no":14,"k":"하나","e":"1 (pure Korean)","s":"하나, 둘, 셋!","lv":1},
{"no":15,"k":"둘","e":"2 (pure Korean)","s":"사과 둘 주세요.","lv":1},
{"no":16,"k":"셋","e":"3 (pure Korean)","s":"셋까지 세요.","lv":1},
{"no":17,"k":"넷","e":"4 (pure Korean)","s":"사람이 넷이에요.","lv":1},
{"no":18,"k":"다섯","e":"5 (pure Korean)","s":"다섯 명이요.","lv":1},
{"no":19,"k":"여섯","e":"6 (pure Korean)","s":"여섯 시에 만나요.","lv":1},
{"no":20,"k":"일곱","e":"7 (pure Korean)","s":"일곱 살이에요.","lv":1},
{"no":21,"k":"여덟","e":"8 (pure Korean)","s":"여덟 개 있어요.","lv":1},
{"no":22,"k":"아홉","e":"9 (pure Korean)","s":"아홉 시에 자요.","lv":1},
{"no":23,"k":"열","e":"10 (pure Korean)","s":"열 살이에요.","lv":1},
{"no":24,"k":"몇","e":"how many / what number","s":"몇 시예요?","lv":1},
{"no":25,"k":"번","e":"number / turn","s":"몇 번이에요?","lv":2},
]},
{"id":6,"ko":"🕐 시간 & 장소","en":"Time & Place","color":"#0ea5e9","short":"시간","lv_min":1,"lv_max":2,"words":[
{"no":1,"k":"지금","e":"now","s":"지금 몇 시예요?","lv":1},
{"no":2,"k":"오늘","e":"today","s":"오늘 뭐 해요?","lv":1},
{"no":3,"k":"내일","e":"tomorrow","s":"내일 만나요.","lv":1},
{"no":4,"k":"어제","e":"yesterday","s":"어제 영화 봤어요.","lv":1},
{"no":5,"k":"아침","e":"morning","s":"아침에 커피 마셔요.","lv":1},
{"no":6,"k":"점심","e":"lunch / noon","s":"점심 먹었어요?","lv":1},
{"no":7,"k":"저녁","e":"evening / dinner","s":"저녁에 만나요.","lv":1},
{"no":8,"k":"밤","e":"night","s":"밤에 자요.","lv":1},
{"no":9,"k":"아까","e":"a moment ago / earlier","s":"아까 전화했어요.","lv":1},
{"no":10,"k":"나중에","e":"later","s":"나중에 다시 전화해요.","lv":1},
{"no":11,"k":"언제","e":"when","s":"언제 와요?","lv":1},
{"no":12,"k":"자주","e":"often / frequently","s":"자주 운동해요.","lv":2},
{"no":13,"k":"어디","e":"where","s":"어디 가요?","lv":1},
{"no":14,"k":"왜","e":"why","s":"왜 안 왔어요?","lv":1},
{"no":15,"k":"어떻게","e":"how","s":"어떻게 가요?","lv":1},
{"no":16,"k":"서울","e":"Seoul","s":"서울에 살아요.","lv":1},
{"no":17,"k":"부산","e":"Busan","s":"부산에 바다가 있어요.","lv":1},
{"no":18,"k":"제주도","e":"Jeju Island","s":"제주도에 여행 갔어요.","lv":1},
{"no":19,"k":"아직","e":"still / not yet","s":"아직 안 왔어요.","lv":2},
{"no":20,"k":"시간","e":"time / hour","s":"시간이 없어요.","lv":1},
{"no":21,"k":"분","e":"minute","s":"십 분 기다려요.","lv":1},
{"no":22,"k":"여기","e":"here","s":"여기 앉아요.","lv":1},
{"no":23,"k":"저기","e":"over there","s":"저기 있어요.","lv":1},
{"no":24,"k":"거기","e":"there","s":"거기에 뭐 있어요?","lv":1},
]},
{"id":7,"ko":"⚡ 동사 활용","en":"Action Verbs (Advanced)","color":"#f97316","short":"동사②","lv_min":1,"lv_max":2,"words":[
{"no":1,"k":"입다","e":"to wear (clothes)","s":"오늘 뭐 입어요?","lv":1},
{"no":2,"k":"만나다","e":"to meet","s":"친구를 만나요.","lv":1},
{"no":3,"k":"듣다","e":"to listen / hear","s":"음악을 들어요.","lv":1},
{"no":4,"k":"운동하다","e":"to exercise","s":"매일 운동해요.","lv":1},
{"no":5,"k":"운전하다","e":"to drive","s":"차를 운전해요.","lv":2},
{"no":6,"k":"쉬다","e":"to rest","s":"집에서 쉬어요.","lv":1},
{"no":7,"k":"조심하다","e":"to be careful","s":"길을 건널 때 조심하세요.","lv":2},
{"no":8,"k":"돕다","e":"to help","s":"친구를 도와요.","lv":2},
{"no":9,"k":"시작하다","e":"to start / begin","s":"수업이 시작해요.","lv":1},
{"no":10,"k":"보내다","e":"to send","s":"메시지를 보내요.","lv":2},
{"no":11,"k":"배우다","e":"to learn","s":"한국어를 배워요.","lv":1},
{"no":12,"k":"열다","e":"to open","s":"문을 열어요.","lv":1},
{"no":13,"k":"닫다","e":"to close","s":"창문을 닫아요.","lv":1},
{"no":14,"k":"가르치다","e":"to teach","s":"학생들에게 영어를 가르쳐요.","lv":2},
{"no":15,"k":"고치다","e":"to fix / repair","s":"컴퓨터를 고쳐요.","lv":2},
{"no":16,"k":"잡다","e":"to catch / grab","s":"버스를 잡아요.","lv":2},
{"no":17,"k":"준비하다","e":"to prepare","s":"여행을 준비해요.","lv":2},
{"no":18,"k":"주문하다","e":"to order","s":"음식을 주문해요.","lv":1},
{"no":19,"k":"걱정하다","e":"to worry","s":"걱정하지 마세요.","lv":2},
{"no":20,"k":"앉다","e":"to sit","s":"여기 앉아요.","lv":1},
{"no":21,"k":"서다","e":"to stand","s":"줄을 서요.","lv":1},
{"no":22,"k":"달리다","e":"to run","s":"공원에서 달려요.","lv":1},
{"no":23,"k":"수영하다","e":"to swim","s":"바다에서 수영해요.","lv":1},
{"no":24,"k":"받다","e":"to receive","s":"선물을 받았어요.","lv":1},
{"no":25,"k":"주다","e":"to give","s":"친구에게 선물을 줬어요.","lv":1},
]},
{"id":8,"ko":"📦 명사 심화","en":"Nouns & People","color":"#14b8a6","short":"명사②","lv_min":1,"lv_max":2,"words":[
{"no":1,"k":"지갑","e":"wallet","s":"지갑을 잃어버렸어요.","lv":1},
{"no":2,"k":"연필","e":"pencil","s":"연필로 써요.","lv":1},
{"no":3,"k":"공","e":"ball","s":"공을 차요.","lv":1},
{"no":4,"k":"나무","e":"tree","s":"나무가 커요.","lv":1},
{"no":5,"k":"이름","e":"name","s":"이름이 뭐예요?","lv":1},
{"no":6,"k":"여동생","e":"younger sister","s":"여동생이 귀여워요.","lv":1},
{"no":7,"k":"은행","e":"bank","s":"은행에서 돈을 찾아요.","lv":1},
{"no":8,"k":"택시","e":"taxi","s":"택시를 타요.","lv":1},
{"no":9,"k":"미국","e":"America / USA","s":"미국에서 왔어요.","lv":1},
{"no":10,"k":"일본","e":"Japan","s":"일본 음식을 좋아해요.","lv":1},
{"no":11,"k":"중국","e":"China","s":"중국어를 배워요.","lv":1},
{"no":12,"k":"영어","e":"English (language)","s":"영어를 가르쳐요.","lv":1},
{"no":13,"k":"한국어","e":"Korean (language)","s":"한국어를 배워요.","lv":1},
{"no":14,"k":"컴퓨터","e":"computer","s":"컴퓨터로 일해요.","lv":1},
{"no":15,"k":"오른쪽","e":"right side","s":"오른쪽으로 가세요.","lv":1},
{"no":16,"k":"왼쪽","e":"left side","s":"왼쪽에 있어요.","lv":1},
{"no":17,"k":"수영","e":"swimming","s":"수영을 잘해요.","lv":1},
{"no":18,"k":"음악","e":"music","s":"음악을 들어요.","lv":1},
{"no":19,"k":"영화","e":"movie / film","s":"영화를 봐요.","lv":1},
{"no":20,"k":"사진","e":"photo / picture","s":"사진을 찍어요.","lv":1},
{"no":21,"k":"편지","e":"letter","s":"친구에게 편지를 써요.","lv":1},
{"no":22,"k":"선물","e":"gift / present","s":"생일 선물이에요.","lv":1},
]},
{"id":9,"ko":"✨ 형용사","en":"Adjectives & Feelings","color":"#a855f7","short":"형용사","lv_min":1,"lv_max":2,"words":[
{"no":1,"k":"좋다","e":"to be good","s":"날씨가 좋아요.","lv":1},
{"no":2,"k":"좋아하다","e":"to like","s":"한국 음식을 좋아해요.","lv":1},
{"no":3,"k":"싫다","e":"to dislike","s":"매운 음식이 싫어요.","lv":2},
{"no":4,"k":"예쁘다","e":"to be pretty","s":"꽃이 예뻐요.","lv":1},
{"no":5,"k":"슬프다","e":"to be sad","s":"영화가 슬퍼요.","lv":2},
{"no":6,"k":"피곤하다","e":"to be tired","s":"오늘 많이 피곤해요.","lv":1},
{"no":7,"k":"건강하다","e":"to be healthy","s":"건강하게 살고 싶어요.","lv":2},
{"no":8,"k":"크다","e":"to be big / large","s":"저 건물이 커요.","lv":1},
{"no":9,"k":"작다","e":"to be small","s":"이 가방은 작아요.","lv":1},
{"no":10,"k":"어렵다","e":"to be difficult","s":"한국어가 어려워요.","lv":2},
{"no":11,"k":"쉽다","e":"to be easy","s":"이 문제는 쉬워요.","lv":1},
{"no":12,"k":"비싸다","e":"to be expensive","s":"이 가방이 비싸요.","lv":1},
{"no":13,"k":"싸다","e":"to be cheap","s":"이 식당이 싸요.","lv":1},
{"no":14,"k":"빠르다","e":"to be fast","s":"기차가 빨라요.","lv":1},
{"no":15,"k":"느리다","e":"to be slow","s":"거북이가 느려요.","lv":2},
{"no":16,"k":"춥다","e":"to be cold (weather)","s":"오늘 너무 추워요.","lv":1},
{"no":17,"k":"덥다","e":"to be hot (weather)","s":"여름에 더워요.","lv":1},
{"no":18,"k":"조금","e":"a little / a bit","s":"조금만 주세요.","lv":1},
{"no":19,"k":"정말","e":"really / truly","s":"정말 맛있어요!","lv":1},
{"no":20,"k":"진짜","e":"really / for real","s":"진짜요?","lv":1},
{"no":21,"k":"아주","e":"very","s":"아주 좋아요.","lv":1},
{"no":22,"k":"별로","e":"not really","s":"별로 안 좋아요.","lv":2},
{"no":23,"k":"전혀","e":"not at all","s":"전혀 몰랐어요.","lv":2},
{"no":24,"k":"잘하다","e":"to be good at","s":"노래를 잘해요.","lv":1},
{"no":25,"k":"못하다","e":"to be bad at","s":"요리를 못해요.","lv":1},
]},
{"id":10,"ko":"📅 요일 & 날짜","en":"Days, Months & Time","color":"#06b6d4","short":"요일","lv_min":1,"lv_max":2,"words":[
{"no":1,"k":"월요일","e":"Monday","s":"월요일에 학교 가요.","lv":1},
{"no":2,"k":"화요일","e":"Tuesday","s":"화요일에 운동해요.","lv":1},
{"no":3,"k":"수요일","e":"Wednesday","s":"수요일에 한국어 수업이 있어요.","lv":1},
{"no":4,"k":"목요일","e":"Thursday","s":"목요일에 친구를 만나요.","lv":1},
{"no":5,"k":"금요일","e":"Friday","s":"금요일이 좋아요.","lv":1},
{"no":6,"k":"토요일","e":"Saturday","s":"토요일에 쉬어요.","lv":1},
{"no":7,"k":"일요일","e":"Sunday","s":"일요일에 교회 가요.","lv":1},
{"no":8,"k":"요일","e":"day of the week","s":"무슨 요일이에요?","lv":1},
{"no":9,"k":"1월","e":"January","s":"1월에 눈이 와요.","lv":1},
{"no":10,"k":"2월","e":"February","s":"2월에 발렌타인데이가 있어요.","lv":1},
{"no":11,"k":"3월","e":"March","s":"3월에 봄이 시작해요.","lv":1},
{"no":12,"k":"4월","e":"April","s":"4월에 벚꽃이 피어요.","lv":1},
{"no":13,"k":"5월","e":"May","s":"5월에 어린이날이 있어요.","lv":1},
{"no":14,"k":"6월","e":"June","s":"6월에 여름이 시작해요.","lv":1},
{"no":15,"k":"7월","e":"July","s":"7월이 가장 더워요.","lv":1},
{"no":16,"k":"8월","e":"August","s":"8월에 방학이에요.","lv":1},
{"no":17,"k":"9월","e":"September","s":"9월에 학교가 시작해요.","lv":1},
{"no":18,"k":"10월","e":"October","s":"10월에 한글날이 있어요.","lv":1},
{"no":19,"k":"11월","e":"November","s":"11월에 날씨가 추워요.","lv":1},
{"no":20,"k":"12월","e":"December","s":"12월에 크리스마스가 있어요.","lv":1},
{"no":21,"k":"매일","e":"every day","s":"매일 운동해요.","lv":1},
{"no":22,"k":"날짜","e":"date","s":"오늘 날짜가 뭐예요?","lv":1},
{"no":23,"k":"어젯밤","e":"last night","s":"어젯밤에 잘 잤어요?","lv":2},
{"no":24,"k":"한 시","e":"one o'clock","s":"한 시에 만나요.","lv":1},
{"no":25,"k":"두 시","e":"two o'clock","s":"두 시에 밥 먹어요.","lv":1},
]},
{"id":11,"ko":"🍽️ 식당 표현","en":"At the Restaurant","color":"#f97316","short":"식당","lv_min":1,"lv_max":2,"words":[
{"no":1,"k":"어서 오세요","e":"welcome! (restaurant/shop)","s":"어서 오세요! 몇 분이세요?","lv":1},
{"no":2,"k":"몇 분이세요?","e":"how many people?","s":"안녕하세요, 몇 분이세요?","lv":1},
{"no":3,"k":"메뉴판 주세요","e":"please give me the menu","s":"저기요, 메뉴판 주세요.","lv":1},
{"no":4,"k":"추천해 주세요","e":"please recommend something","s":"뭐가 맛있어요? 추천해 주세요.","lv":1},
{"no":5,"k":"주문할게요","e":"I'd like to order","s":"저기요, 주문할게요!","lv":1},
{"no":6,"k":"이거 주세요","e":"I'll have this","s":"이거 두 개 주세요.","lv":1},
{"no":7,"k":"맵지 않게 해주세요","e":"please make it not spicy","s":"저 매운 거 못 먹어요. 맵지 않게 해주세요.","lv":2},
{"no":8,"k":"물 한 잔 주세요","e":"please give me a glass of water","s":"저기요, 물 한 잔 주세요.","lv":1},
{"no":9,"k":"잘 먹겠습니다","e":"said before eating","s":"잘 먹겠습니다!","lv":1},
{"no":10,"k":"잘 먹었습니다","e":"thank you for the meal","s":"정말 맛있었어요. 잘 먹었습니다!","lv":1},
{"no":11,"k":"계산서 주세요","e":"please bring the bill","s":"다 먹었어요. 계산서 주세요.","lv":1},
{"no":12,"k":"포장해 주세요","e":"please pack it to go","s":"다 못 먹겠어요. 포장해 주세요.","lv":1},
{"no":13,"k":"제가 살게요","e":"it's on me / I'll treat you","s":"오늘은 제가 살게요!","lv":2},
{"no":14,"k":"더 주세요","e":"please give me more","s":"김치 더 주세요.","lv":1},
{"no":15,"k":"맛있게 드세요","e":"enjoy your meal","s":"맛있게 드세요!","lv":1},
{"no":16,"k":"리필 돼요?","e":"can I get a refill?","s":"물 리필 돼요?","lv":2},
{"no":17,"k":"따로따로 계산할게요","e":"we'll pay separately","s":"따로따로 계산할게요.","lv":2},
{"no":18,"k":"다음에 또 올게요","e":"I'll come again next time","s":"너무 맛있었어요. 다음에 또 올게요!","lv":2},
]},
{"id":12,"ko":"🗺️ 길 묻기","en":"Asking for Directions","color":"#10b981","short":"길묻기","lv_min":1,"lv_max":2,"words":[
{"no":1,"k":"실례합니다","e":"excuse me","s":"실례합니다, 잠깐 여쭤봐도 될까요?","lv":1},
{"no":2,"k":"어떻게 가요?","e":"how do I get there?","s":"경복궁에 어떻게 가요?","lv":1},
{"no":3,"k":"어디에 있어요?","e":"where is it?","s":"화장실이 어디에 있어요?","lv":1},
{"no":4,"k":"길을 잃었어요","e":"I'm lost","s":"죄송한데요, 길을 잃었어요.","lv":1},
{"no":5,"k":"직진하세요","e":"go straight","s":"저 길로 직진하세요.","lv":1},
{"no":6,"k":"오른쪽으로 가세요","e":"turn right","s":"신호등에서 오른쪽으로 가세요.","lv":1},
{"no":7,"k":"왼쪽으로 가세요","e":"turn left","s":"편의점 앞에서 왼쪽으로 가세요.","lv":1},
{"no":8,"k":"얼마나 걸려요?","e":"how long does it take?","s":"걸어서 얼마나 걸려요?","lv":1},
{"no":9,"k":"가까워요?","e":"is it close?","s":"여기서 가까워요?","lv":1},
{"no":10,"k":"멀어요","e":"it's far","s":"걸어가기엔 멀어요. 버스 타세요.","lv":1},
{"no":11,"k":"지하철역이 어디예요?","e":"where is the subway station?","s":"이 근처에 지하철역이 어디예요?","lv":1},
{"no":12,"k":"버스 정류장","e":"bus stop","s":"버스 정류장이 저기예요.","lv":1},
{"no":13,"k":"이 길이 맞아요?","e":"is this the right way?","s":"홍대 가려면 이 길이 맞아요?","lv":2},
{"no":14,"k":"지도 앱","e":"map app","s":"지도 앱으로 찾아보세요.","lv":1},
{"no":15,"k":"모르겠어요","e":"I'm not sure","s":"저도 이 동네가 낯설어서 모르겠어요.","lv":2},
]},
{"id":13,"ko":"🤝 친해지기","en":"Getting to Know Someone","color":"#8b5cf6","short":"친해지기","lv_min":1,"lv_max":2,"words":[
{"no":1,"k":"어디서 왔어요?","e":"where are you from?","s":"혹시 어디서 왔어요?","lv":1},
{"no":2,"k":"무슨 일 해요?","e":"what do you do for work?","s":"혹시 무슨 일 해요?","lv":1},
{"no":3,"k":"취미가 뭐예요?","e":"what's your hobby?","s":"시간 있을 때 취미가 뭐예요?","lv":1},
{"no":4,"k":"한국어 잘 하시네요","e":"your Korean is great!","s":"와, 한국어 잘 하시네요!","lv":2},
{"no":5,"k":"카카오톡 있어요?","e":"do you have KakaoTalk?","s":"카카오톡 있어요? 연락해요!","lv":1},
{"no":6,"k":"번호 알려줘도 돼요?","e":"can I get your number?","s":"번호 알려줘도 돼요?","lv":2},
{"no":7,"k":"저도요","e":"me too / same here","s":"저도 한국 음식 좋아해요. — 저도요!","lv":1},
{"no":8,"k":"정말요?","e":"really?","s":"한국에 3년 살았어요. — 정말요?","lv":1},
{"no":9,"k":"다음에 또 만나요","e":"let's meet again next time","s":"오늘 정말 즐거웠어요. 다음에 또 만나요!","lv":1},
{"no":10,"k":"연락할게요","e":"I'll contact you","s":"번호 받았어요. 연락할게요!","lv":1},
{"no":11,"k":"친구 해요","e":"let's be friends","s":"우리 친구 해요!","lv":1},
{"no":12,"k":"잘 부탁드려요","e":"nice to meet you / please take care of me","s":"앞으로 잘 부탁드려요.","lv":2},
{"no":13,"k":"재미있는 사람이네요","e":"you're a fun person","s":"와, 재미있는 사람이네요!","lv":2},
{"no":14,"k":"잘 통하는 것 같아요","e":"I feel like we click","s":"얘기하다 보니 잘 통하는 것 같아요.","lv":2},
{"no":15,"k":"얼마나 됐어요?","e":"how long has it been?","s":"한국에 온 지 얼마나 됐어요?","lv":2},
]},
{"id":14,"ko":"💕 데이트","en":"Dating & Polite Rejection","color":"#ec4899","short":"데이트","lv_min":1,"lv_max":2,"words":[
{"no":1,"k":"저랑 밥 먹을래요?","e":"would you like to eat with me?","s":"이번 주말에 저랑 밥 먹을래요?","lv":2},
{"no":2,"k":"같이 영화 볼래요?","e":"would you like to watch a movie together?","s":"같이 영화 볼래요?","lv":2},
{"no":3,"k":"저 당신이 좋아요","e":"I like you","s":"솔직히 말할게요. 저 당신이 좋아요.","lv":2},
{"no":4,"k":"언제 시간 돼요?","e":"when are you free?","s":"이번 주에 언제 시간 돼요?","lv":1},
{"no":5,"k":"좋아요!","e":"sounds good! / yes!","s":"같이 가요? — 좋아요!","lv":1},
{"no":6,"k":"생각해 볼게요","e":"I'll think about it","s":"갑자기 말씀하셔서... 생각해 볼게요.","lv":2},
{"no":7,"k":"다른 사람이 있어요","e":"I'm seeing someone","s":"감사한데요, 이미 다른 사람이 있어요.","lv":2},
{"no":8,"k":"그냥 친구로 지내요","e":"let's just stay friends","s":"그냥 친구로 지내고 싶어요.","lv":2},
{"no":9,"k":"부담 갖지 마세요","e":"don't feel pressured","s":"제 마음만 전하는 거예요. 부담 갖지 마세요.","lv":2},
{"no":10,"k":"오늘 즐거웠어요","e":"I had fun today","s":"오늘 정말 즐거웠어요. 또 만나요!","lv":1},
{"no":11,"k":"맛있는 거 먹으러 가요","e":"let's go eat something delicious","s":"오늘 제가 살게요. 맛있는 거 먹으러 가요!","lv":1},
{"no":12,"k":"어디로 갈까요?","e":"where shall we go?","s":"오늘 데이트 기대돼요. 어디로 갈까요?","lv":2},
]},
{"id":15,"ko":"💼 비즈니스","en":"Business Conversations","color":"#1d4ed8","short":"비즈니스","lv_min":2,"lv_max":3,"words":[
{"no":1,"k":"잘 부탁드립니다","e":"I look forward to working with you","s":"처음 뵙겠습니다. 잘 부탁드립니다.","lv":2},
{"no":2,"k":"명함 드려도 될까요?","e":"may I give you my business card?","s":"잠깐, 명함 드려도 될까요?","lv":2},
{"no":3,"k":"미팅을 잡고 싶어요","e":"I'd like to set up a meeting","s":"다음 주에 미팅을 잡고 싶어요.","lv":2},
{"no":4,"k":"언제 시간 되세요?","e":"when are you available?","s":"이번 주에 언제 시간 되세요?","lv":2},
{"no":5,"k":"미팅을 미뤄도 될까요?","e":"could we postpone the meeting?","s":"급한 일이 생겼어요. 미팅을 미뤄도 될까요?","lv":2},
{"no":6,"k":"검토해 주세요","e":"please review this","s":"시간 되실 때 검토해 주세요.","lv":2},
{"no":7,"k":"담당자가 누구세요?","e":"who is the person in charge?","s":"이 건 담당자가 누구세요?","lv":2},
{"no":8,"k":"연락 드리겠습니다","e":"I'll be in touch","s":"확인 후 연락 드리겠습니다.","lv":2},
{"no":9,"k":"회의실이 어디예요?","e":"where is the meeting room?","s":"3층 회의실이 어디예요?","lv":1},
{"no":10,"k":"참석하겠습니다","e":"I will attend","s":"네, 그 미팅에 참석하겠습니다.","lv":3},
{"no":11,"k":"불참하게 됐어요","e":"I'm unable to attend","s":"죄송하게도 불참하게 됐어요.","lv":3},
{"no":12,"k":"말씀 많이 들었어요","e":"I've heard a lot about you","s":"안녕하세요, 말씀 많이 들었어요.","lv":2},
{"no":13,"k":"바쁘신데 시간 내주셔서 감사합니다","e":"thank you for making time","s":"바쁘신데 시간 내주셔서 감사합니다.","lv":3},
{"no":14,"k":"제안서를 보내드릴게요","e":"I'll send you the proposal","s":"내일까지 제안서를 보내드릴게요.","lv":3},
]},
{"id":16,"ko":"🎬 드라마 & 감탄","en":"K-Drama & Movie Reactions","color":"#7c3aed","short":"드라마","lv_min":1,"lv_max":2,"words":[
{"no":1,"k":"대박!","e":"oh wow! / amazing! (slang)","s":"이 드라마 진짜 대박이에요!","lv":1},
{"no":2,"k":"완전 재밌어요","e":"it's so fun / really entertaining","s":"이 드라마 완전 재밌어요. 강추예요!","lv":1},
{"no":3,"k":"강추예요","e":"highly recommended","s":"이 영화 강추예요. 꼭 보세요!","lv":2},
{"no":4,"k":"꼭 보세요","e":"you have to watch it","s":"이번 시즌 꼭 보세요, 진짜 최고예요.","lv":1},
{"no":5,"k":"눈물 났어요","e":"I cried","s":"마지막 장면에서 눈물 났어요.","lv":1},
{"no":6,"k":"너무 감동적이에요","e":"it's so touching / moving","s":"그 장면 너무 감동적이에요.","lv":2},
{"no":7,"k":"반전이 있어요","e":"there's a plot twist","s":"이 영화 끝에 반전이 있어요.","lv":2},
{"no":8,"k":"다음 편이 기대돼요","e":"I can't wait for the next episode","s":"다음 편이 기대돼요!","lv":2},
{"no":9,"k":"정주행했어요","e":"I binge-watched it","s":"주말에 정주행했어요. 진짜 최고예요.","lv":2},
{"no":10,"k":"밤새 봤어요","e":"I watched it all night","s":"너무 재밌어서 밤새 봤어요.","lv":1},
{"no":11,"k":"실망했어요","e":"I was disappointed","s":"기대가 컸는데 좀 실망했어요.","lv":2},
{"no":12,"k":"연기를 너무 잘해요","e":"they act so well","s":"주인공 연기를 너무 잘해요!","lv":2},
{"no":13,"k":"OST가 너무 좋아요","e":"the OST is so good","s":"이 드라마 OST가 너무 좋아요.","lv":1},
{"no":14,"k":"결말이 좋았어요","e":"the ending was good","s":"결말이 좋았어요. 해피엔딩이에요.","lv":2},
{"no":15,"k":"어디서 봤어요?","e":"where did you watch it?","s":"이 드라마 어디서 봤어요? 넷플릭스예요?","lv":1},
{"no":16,"k":"지금 방영 중이에요","e":"it's currently airing","s":"매주 수목에 방영 중이에요.","lv":2},
]},
]

# ── 기존 카테고리에서 이미 다룬 한국어 단어 집합 ──────────────────────────────
COVERED_KO = set()
for cat in EXISTING_DATA:
    for w in cat["words"]:
        COVERED_KO.add(w["k"])

# ── 1-2급 TOPIK 단어 중 미포함 단어 추출 ─────────────────────────────────────
topik_12 = [w for w in all_words if w["level"] in (1, 2)]
remaining_12 = [w for w in topik_12 if w["word"] not in COVERED_KO]
print(f"1-2급 전체: {len(topik_12)}개  |  기존 카테고리 미포함: {len(remaining_12)}개")

# ─────────────────────────────────────────────────────────────────────────────
# 시나리오 기반 1-2급 카테고리 (scenario_tags_v2.json)
# ─────────────────────────────────────────────────────────────────────────────

# 시나리오 정의 (sid, ko, en, color)
SCENARIO_DEFS = [
    ("S01",  "😊 감정 & 심리",    "Emotions & Psychology",   "#fb7185"),
    ("S02",  "💭 생각 & 말하기",  "Speaking & Thinking",     "#f97316"),
    ("S03",  "👥 관계 & 예절",    "Relationships & Manners", "#fbbf24"),
    ("S04",  "🌍 장소 & 방향",    "Places & Directions",     "#34d399"),
    ("S05",  "⏰ 시간 & 순서",    "Time & Sequence",         "#06b6d4"),
    ("S06",  "🔄 행동 & 변화",    "Actions & Changes",       "#818cf8"),
    ("S07a", "🎨 색깔 & 외모",    "Colors & Appearance",     "#f472b6"),
    ("S07b", "📏 크기 & 비교",    "Size & Comparison",       "#38bdf8"),
    ("S07c", "🧠 성격 & 특성",    "Personality & Traits",    "#a78bfa"),
    ("S08",  "🌱 자연 & 계절",    "Nature & Seasons",        "#4ade80"),
    ("S09",  "🛒 쇼핑 & 소비",    "Shopping & Consumer",     "#fb923c"),
    ("S10",  "🍽️ 식재료 & 요리", "Ingredients & Cooking",   "#f59e0b"),
    ("S11",  "🏃 건강 & 신체",    "Health & Body",           "#f43f5e"),
    ("S12",  "📚 학교 & 학습",    "School & Study",          "#3b82f6"),
    ("S13",  "🎭 취미 & 여가",    "Hobbies & Leisure",       "#8b5cf6"),
    ("S14",  "🏠 집 & 주거",      "Home & Living",           "#10b981"),
    ("S15",  "🚌 교통 & 이동",    "Transport & Travel",      "#6366f1"),
    ("S16",  "🔗 연결어 & 부사",  "Connectors & Adverbs",    "#64748b"),
    ("NUM",  "🔢 숫자 & 단위",    "Numbers & Units",         "#94a3b8"),
]

# 시나리오 태그 로드
scenario_json = json.loads((BASE / "scenario_tags_v2.json").read_text(encoding="utf-8"))
SCENARIO_TAGS = scenario_json["tagged"]  # {word: scenario_id}

# remaining_12 단어를 시나리오별 버킷에 분류
scenario_buckets = defaultdict(list)
untagged_words = []
for w in remaining_12:
    sid = SCENARIO_TAGS.get(w["word"])
    if sid:
        scenario_buckets[sid].append(w)
    else:
        untagged_words.append(w)

print("\n=== 시나리오별 1-2급 잔여 단어 분류 ===")
for sid, ko, en, color in SCENARIO_DEFS:
    n = len(scenario_buckets.get(sid, []))
    if n:
        print(f"  {ko:20} ({sid}): {n:3}개")
if untagged_words:
    print(f"  [미태깅]:                    {len(untagged_words):3}개")

def make_word_entry(w, no):
    meaning, ex_ko, ex_en = word_data(w)
    return {
        "no": no,
        "k":  w["word"],
        "e":  meaning or w["word"],
        "s":  ex_ko or "",
        "se": ex_en or "",
        "lv": w["level"],
        "pos": w["pos_en"],
    }

# ── 시나리오 카테고리 구축 (Cat 17~) ─────────────────────────────────────────
NEW_DATA_12 = []
_next_cat_id = [17]  # mutable counter

def _add_scenario_cat(sid, ko, en, color, words):
    if not words:
        return
    cat_id = _next_cat_id[0]
    _next_cat_id[0] += 1
    entries = [make_word_entry(w, i+1) for i, w in enumerate(words)]
    short = ko.split(" ")[-1] if " " in ko else ko
    NEW_DATA_12.append({
        "id":    cat_id,
        "ko":    ko,
        "en":    en,
        "color": color,
        "short": short,
        "lv_min": 1,
        "lv_max": 2,
        "words": entries,
    })
    print(f"  카테고리 {cat_id} [{ko}]: {len(entries)}단어")

for sid, ko, en, color in SCENARIO_DEFS:
    _add_scenario_cat(sid, ko, en, color, scenario_buckets.get(sid, []))

# 미태깅 단어 → 기타 카테고리 (있는 경우)
if untagged_words:
    _add_scenario_cat("ETC", "📝 기타 어휘", "Other Vocabulary", "#94a3b8", untagged_words)


# ── 3-6급 레벨별 카테고리 ─────────────────────────────────────────────────────
LEVEL_COLORS = {3:"#16a34a", 4:"#2563eb", 5:"#9333ea", 6:"#dc2626"}
LEVEL_EMOJI  = {3:"📗", 4:"📘", 5:"📙", 6:"📕"}
LEVEL_NAMES  = {3:"초중급", 4:"중급", 5:"중고급", 6:"고급"}

LEVEL_DATA = []
cat_id = 17 + len(NEW_DATA_12)  # 기존 16 + 시나리오 수
for lv in range(3, 7):
    lv_words = [w for w in all_words if w["level"] == lv]
    color    = LEVEL_COLORS[lv]
    emoji    = LEVEL_EMOJI[lv]
    lv_name  = LEVEL_NAMES[lv]

    # POS 그룹 분류
    nouns   = [w for w in lv_words if w["pos_en"] in ("noun","bound noun","pronoun","numeral")]
    verbs   = [w for w in lv_words if w["pos_en"] in ("verb","adjective")]
    others  = [w for w in lv_words if w not in nouns and w not in verbs]

    groups = [
        (f"{emoji} {lv}급 명사",       f"TOPIK {lv} · Nouns ({lv_name})",       nouns),
        (f"{emoji} {lv}급 동사/형용사", f"TOPIK {lv} · Verbs & Adj. ({lv_name})", verbs),
        (f"{emoji} {lv}급 부사/기타",   f"TOPIK {lv} · Adverbs & More ({lv_name})", others),
    ]
    for ko, en, wlist in groups:
        if not wlist:
            continue
        entries = [make_word_entry(w, i+1) for i, w in enumerate(wlist)]
        short   = f"{lv}급{'명사' if '명사' in ko else '동형' if '동사' in ko else '기타'}"
        LEVEL_DATA.append({
            "id":    cat_id,
            "ko":    ko,
            "en":    en,
            "color": color,
            "short": short,
            "lv_min": lv,
            "lv_max": lv,
            "words": entries,
        })
        print(f"  카테고리 {cat_id} [{ko}]: {len(entries)}단어")
        cat_id += 1

# ── 전체 DATA 합치기 ──────────────────────────────────────────────────────────
ALL_DATA = EXISTING_DATA + NEW_DATA_12 + LEVEL_DATA
total_words = sum(len(c["words"]) for c in ALL_DATA)
print(f"\n총 카테고리: {len(ALL_DATA)}개  |  총 단어: {total_words}개")

# ─────────────────────────────────────────────────────────────────────────────
# HTML 생성: TOPIK_I_v3.html의 DATA 부분을 교체
# ─────────────────────────────────────────────────────────────────────────────
with open(BASE / "TOPIK_I_v3.html", encoding="utf-8") as f:
    html = f.read()

# DATA 교체
data_json = json.dumps(ALL_DATA, ensure_ascii=False, separators=(",",":"))
# const DATA=[...]; 패턴 찾아 교체
html = re.sub(r'const DATA=\[.*?\];', f'const DATA={data_json};', html, flags=re.DOTALL)

# 통계 텍스트 업데이트
total_cats = len(ALL_DATA)
html = re.sub(r'339단어 · 16 카테고리',
              f'{total_words:,}단어 · {total_cats} 카테고리', html)
html = re.sub(r"<div class=\"n\">16</div><div class=\"l\">카테고리",
              f'<div class="n">{total_cats}</div><div class="l">카테고리', html)
html = re.sub(r'TOPIK Level 1–2 · \d+단어 · \d+ 카테고리',
              f'TOPIK Level 1–6 · {total_words:,}단어 · {total_cats} 카테고리', html)
html = re.sub(r'TOPIK 1-2급 단어장',
              'TOPIK 1-6급 단어장', html)
html = html.replace('TOPIK Level 1–2', 'TOPIK Level 1–6')

# ── 레벨 필터 버튼 UI 추가 ──────────────────────────────────────────────────
# 기존 레벨 필터(LF) 버튼 블록 찾아 교체 (없으면 추가)
LEVEL_FILTER_CSS = """
/* ─── LEVEL FILTER ─── */
#lf-bar{display:flex;gap:5px;flex-wrap:wrap;padding:10px 12px 8px;
  border-bottom:1px solid var(--brd);background:var(--surf)}
.lf-btn{flex:1;min-width:40px;padding:5px 3px;border-radius:20px;font-size:.71rem;
  font-weight:700;border:1.5px solid var(--brd2);background:var(--surf2);
  color:var(--tx2);cursor:pointer;text-align:center;transition:.15s}
.lf-btn:hover:not(.active){background:var(--al);border-color:var(--am)}
.lf-btn[data-lv="0"].active{background:#6366f1;color:#fff;border-color:#6366f1}
.lf-btn[data-lv="12"].active{background:#6366f1;color:#fff;border-color:#6366f1}
.lf-btn[data-lv="3"].active{background:#16a34a;color:#fff;border-color:#16a34a}
.lf-btn[data-lv="4"].active{background:#2563eb;color:#fff;border-color:#2563eb}
.lf-btn[data-lv="5"].active{background:#9333ea;color:#fff;border-color:#9333ea}
.lf-btn[data-lv="6"].active{background:#dc2626;color:#fff;border-color:#dc2626}
/* ─── LEVEL CHIP ─── */
.lv-chip{display:inline-block;font-size:.6rem;font-weight:800;padding:1px 5px;
  border-radius:10px;color:#fff;margin-left:4px;vertical-align:middle;line-height:1.5}
.lv-chip.lv12{background:#6366f1}.lv-chip.lv1{background:#6366f1}.lv-chip.lv2{background:#6366f1}
.lv-chip.lv3{background:#16a34a}.lv-chip.lv4{background:#2563eb}
.lv-chip.lv5{background:#9333ea}.lv-chip.lv6{background:#dc2626}
/* ─── SECTION HEADER ─── */
.sb-sec{padding:8px 14px 5px;font-size:.7rem;font-weight:800;letter-spacing:.03em;
  text-transform:uppercase;color:#fff;margin-top:4px}
.sb-sec.sec12{background:linear-gradient(90deg,#6366f1,#818cf8)}
.sb-sec.sec3{background:linear-gradient(90deg,#16a34a,#22c55e)}
.sb-sec.sec4{background:linear-gradient(90deg,#2563eb,#60a5fa)}
.sb-sec.sec5{background:linear-gradient(90deg,#9333ea,#c084fc)}
.sb-sec.sec6{background:linear-gradient(90deg,#dc2626,#f87171)}
"""

LEVEL_FILTER_HTML = """
<div id="lf-bar">
  <button class="lf-btn active" data-lv="0" onclick="setLF(0,this)">전체</button>
  <button class="lf-btn" data-lv="12" onclick="setLF(12,this)">1-2급</button>
  <button class="lf-btn" data-lv="3" onclick="setLF(3,this)">3급</button>
  <button class="lf-btn" data-lv="4" onclick="setLF(4,this)">4급</button>
  <button class="lf-btn" data-lv="5" onclick="setLF(5,this)">5급</button>
  <button class="lf-btn" data-lv="6" onclick="setLF(6,this)">6급</button>
</div>
"""

LEVEL_FILTER_JS = """
// ── LEVEL FILTER ──────────────────────────────────────────────────────────
let LF_ACTIVE = (()=>{ try{ return parseInt(localStorage.getItem('bwk_lf')||'0'); }catch(e){return 0;} })();
function setLF(lv, btn){
  LF_ACTIVE = lv;
  try{ localStorage.setItem('bwk_lf', lv); }catch(e){}
  document.querySelectorAll('.lf-btn').forEach(b=>b.classList.remove('active'));
  btn.classList.add('active');
  renderSidebar();
}
function catMatchesLF(cat){
  if(LF_ACTIVE===0) return true;
  if(LF_ACTIVE===12) return (cat.lv_min||1) <= 2 && (cat.lv_max||6) >= 1;
  return (cat.lv_min||1) <= LF_ACTIVE && (cat.lv_max||6) >= LF_ACTIVE;
}
"""

# 새 renderSidebar 함수 (레벨 그룹 동적 렌더링)
NEW_RENDER_SIDEBAR = r"""function renderSidebar() {
  const LV_COLORS = {12:'#6366f1',1:'#6366f1',2:'#6366f1',3:'#16a34a',4:'#2563eb',5:'#9333ea',6:'#dc2626'};
  const renderLvChip = c => {
    const mn = c.lv_min||1, mx = c.lv_max||2;
    const key = (mn===1&&mx===2)?'12':(mn===mx?mn:mn);
    const label = (mn===1&&mx===2)?'1-2급':(mn===mx?mn+'급':mn+'-'+mx+'급');
    const cls = (mn===1&&mx===2)?'lv12':('lv'+mn);
    return `<span class="lv-chip ${cls}">${label}</span>`;
  };
  const renderCatItem = c => {
    const {done,sets} = catDone(c);
    const badge = done===sets&&sets>0
      ? '<span style="font-size:.65rem;color:#16a34a;font-weight:700">✓완료</span>'
      : done>0 ? `<span style="font-size:.65rem;color:var(--a);font-weight:700">${done}/${sets}</span>` : '';
    const total=c.words.length; let m0=0,m1=0,m2=0;
    c.words.forEach(w=>{const lv=getMastery(c.id,w.no);if(lv===2)m2++;else if(lv===1)m1++;else m0++;});
    const p2=Math.round(m2/total*100),p1=Math.round(m1/total*100),p0=100-p2-p1;
    const prog=`<div class="cprog" style="display:flex">`
      +`<div style="width:${p2}%;background:#10b981;border-radius:2px 0 0 2px;height:100%"></div>`
      +`<div style="width:${p1}%;background:#f59e0b;height:100%"></div>`
      +`<div style="width:${p0}%;background:#e5e7eb;border-radius:0 2px 2px 0;height:100%"></div></div>`;
    return `<div class="ci" id="ci${c.id}" style="--cc:${c.color}" onclick="showCat(${c.id})" role="button" tabindex="0" aria-label="${c.ko}" onkeydown="if(event.key==='Enter')showCat(${c.id})">
      <div class="cn">${c.id}</div>
      <div class="cl">
        <div class="cko">${c.ko}${renderLvChip(c)}</div>
        <div class="cen">${c.en}</div>
        ${prog}
      </div>
      <div class="cnt" title="${Math.round(m2/total*100)}% 완료">${badge||c.words.length+'단어'}</div>
    </div>`;
  };

  // 레벨 필터 버튼 렌더링
  const lfBar = `<div id="lf-bar">
    <button class="lf-btn${LF_ACTIVE===0?' active':''}" data-lv="0" onclick="setLF(0,this)">전체</button>
    <button class="lf-btn${LF_ACTIVE===12?' active':''}" data-lv="12" onclick="setLF(12,this)">1-2급</button>
    <button class="lf-btn${LF_ACTIVE===3?' active':''}" data-lv="3" onclick="setLF(3,this)">3급</button>
    <button class="lf-btn${LF_ACTIVE===4?' active':''}" data-lv="4" onclick="setLF(4,this)">4급</button>
    <button class="lf-btn${LF_ACTIVE===5?' active':''}" data-lv="5" onclick="setLF(5,this)">5급</button>
    <button class="lf-btn${LF_ACTIVE===6?' active':''}" data-lv="6" onclick="setLF(6,this)">6급</button>
  </div>`;

  // 카테고리 필터링
  const visible = DATA.filter(c => catMatchesLF(c));

  // 레벨 섹션 그룹
  const SECTIONS = [
    {label:'📚 1-2급 기초·표현', min:1, max:2, cls:'sec12'},
    {label:'📗 3급 초중급',      min:3, max:3, cls:'sec3'},
    {label:'📘 4급 중급',        min:4, max:4, cls:'sec4'},
    {label:'📙 5급 중고급',      min:5, max:5, cls:'sec5'},
    {label:'📕 6급 고급',        min:6, max:6, cls:'sec6'},
  ];

  let html = lfBar;
  SECTIONS.forEach(sec => {
    const cats = visible.filter(c => (c.lv_min||1) <= sec.max && (c.lv_max||6) >= sec.min);
    if(!cats.length) return;
    html += `<div class="sb-sec ${sec.cls}">${sec.label}</div>` + cats.map(renderCatItem).join('');
  });

  html += `<div class="ci" id="ci-trivia" style="--cc:#f59e0b" onclick="showTriviaCat()" role="button" tabindex="0" aria-label="K-Culture Trivia" onkeydown="if(event.key==='Enter')showTriviaCat()">
      <div class="cn">★</div>
      <div class="cl">
        <div class="cko">🌟 K-Culture Trivia</div>
        <div class="cen">K-POP · K-FOOD · K-DRAMA · K-CELEB · K-TRAVEL</div>
      </div>
      <div class="cnt">245문제</div>
    </div>`;

  document.getElementById('clist').innerHTML = html;
}"""

# CSS 주입
if "LEVEL FILTER" not in html:
    html = html.replace("/* ─── CONFETTI ─── */",
                        LEVEL_FILTER_CSS + "\n/* ─── CONFETTI ─── */")

# LF 변수 선언 제거 (구 버전)
html = re.sub(r'let LF\s*=\s*\d+;[^\n]*\n', '', html)

# 기존 setLF 함수 교체 또는 신규 추가
if 'function setLF(' in html:
    # 기존 한 줄짜리 setLF 교체
    html = re.sub(r'function setLF\([^)]*\)\s*\{[^}]*\}',
                  LEVEL_FILTER_JS.strip(), html)
else:
    html = html.replace('const ADMIN_EMAIL', LEVEL_FILTER_JS + '\nconst ADMIN_EMAIL')

# renderSidebar 함수 전체 교체
OLD_RS = re.search(r'function renderSidebar\(\).*?^\}', html, re.DOTALL | re.MULTILINE)
if OLD_RS:
    html = html[:OLD_RS.start()] + NEW_RENDER_SIDEBAR + html[OLD_RS.end():]
    print("  ✅ renderSidebar 교체 완료")
else:
    print("  ⚠️ renderSidebar 찾지 못함 - 수동 확인 필요")

# 타이틀 업데이트
html = html.replace('<title>TOPIK 1-2급 단어장 · Blue Whale Korean</title>',
                    '<title>TOPIK 1-6급 단어장 · Blue Whale Korean</title>')

# 헤더 · 통계 텍스트 업데이트 (old "339단어 · 16 Categories" 등 제거)
new_stats = f'{total_words:,}단어 · {len(ALL_DATA)} Categories'
html = re.sub(r'\d+단어\s*[·•]\s*\d+\s*Categor(?:y|ies)', new_stats, html)
html = re.sub(r'\d+단어\s*[·•]\s*\d+\s*카테고리', f'{total_words:,}단어 · {len(ALL_DATA)} 카테고리', html)
# 남은 단독 "339" 패턴 (id="ws-words">339 등)
html = re.sub(r'(?<=id="ws-words">)\d+', str(total_words), html)
html = re.sub(r'(?<=ws-words">)\d+', str(total_words), html)
# TOPIK 1-2급 → 1-6급 헤더 문자열
html = re.sub(r'TOPIK\s+1[-–]2급', 'TOPIK 1-6급', html)
# 선생님 코멘트 "339개" / "339 단어" 패턴
html = re.sub(r'339\s*개', f'{total_words:,}개', html)
html = re.sub(r'339\s*단어', f'{total_words:,}단어', html)
# 16 카테고리 / 16 Categories
html = re.sub(r'\b16\s*(?:카테고리|Categories)', f'{len(ALL_DATA)} 카테고리', html)
# English teacher note "339 words" → correct count
html = re.sub(r'These \d+ words cover essential TOPIK Level [^<]+',
              f'These {total_words:,} words cover all 6 levels of TOPIK vocabulary — '
              'from everyday basics to advanced expressions. '
              'Start with Level 1–2 scenarios and work your way up!', html)

# ── 퀴즈·카드 세트 버튼 순서: Set 1,2,...N 먼저 → 전체 마지막 ──────────────────

SF_BAR_JS = r"""
// ── SET BAR HELPER: 세트 8개 이하 → 버튼, 초과 → 드롭다운 ────────────────────
function buildSfBar(sets, activeSf, color, clickFn, totalLabel) {
  if (sets <= 8) {
    let h = '';
    for(let s=0;s<sets;s++){
      const isA=activeSf===s, done=getProg(CC.id,s);
      h+=`<button class="sfbtn${isA?' active':''}" style="${isA?'background:'+color+';color:#fff':''}"
        onclick="${clickFn}(${s})">Set ${s+1}${done?' ✓':''}</button>`;
    }
    h+=`<button class="sfbtn${activeSf<0?' active':''}" style="${activeSf<0?'background:'+color+';color:#fff':''}"
      onclick="${clickFn}(-1)">${totalLabel}</button>`;
    return `<div class="sf-bar">${h}</div>`;
  } else {
    const prev = activeSf > 0 ? activeSf-1 : (activeSf<0 ? sets-1 : -1);
    const next = activeSf < sets-1 ? activeSf+1 : (activeSf===sets-1 ? -1 : 0);
    let opts = '';
    for(let s=0;s<sets;s++){
      const done=getProg(CC.id,s);
      opts+=`<option value="${s}"${activeSf===s?' selected':''}>Set ${s+1}${done?' ✓':''}</option>`;
    }
    opts+=`<option value="-1"${activeSf<0?' selected':''}>${totalLabel}</option>`;
    const cur = activeSf < 0 ? '전체' : `Set ${activeSf+1}`;
    return `<div class="sf-bar sf-compact">
      <button class="sfbtn" onclick="${clickFn}(${prev})" title="이전 세트">◀</button>
      <select class="sf-sel" style="border-color:${color}" onchange="${clickFn}(parseInt(this.value))">${opts}</select>
      <button class="sfbtn" onclick="${clickFn}(${next})" title="다음 세트">▶</button>
      <span class="sf-info" style="color:${color}">${cur} · ${CC.words.length}단어</span>
    </div>`;
  }
}
"""

SF_BAR_CSS = """
/* compact set bar (many sets) */
.sf-compact{flex-wrap:nowrap;align-items:center;gap:8px;padding:6px 0}
.sf-compact .sfbtn{padding:5px 10px;min-width:36px}
.sf-sel{flex:1;max-width:160px;padding:5px 8px;border-radius:20px;
  border:2px solid var(--brd2);background:var(--surf2);
  color:var(--tx);font-size:.8rem;font-weight:700;font-family:inherit;cursor:pointer}
.sf-info{font-size:.75rem;font-weight:700;white-space:nowrap}
"""

PATCH_CARD_SF = r"""function renderCardUI() {
  const c=CC, sets=Math.ceil(c.words.length/10);
  document.getElementById('kv').innerHTML = `
    ${buildSfBar(sets, CSF, c.color, 'initCard', '전체 · All ('+c.words.length+')')}
    <div class="dir-bar">"""

PATCH_QUIZ_SF = r"""function renderQuizUI(){
  const c=CC,sets=Math.ceil(c.words.length/10);
  document.getElementById('qv').innerHTML=`
    ${buildSfBar(sets, QSF, c.color, 'initQuiz', '전체 ('+QW.length+')')}
    <div class="qdir">"""

# CSS 주입
if 'sf-compact' not in html:
    html = html.replace('.sf-bar{', SF_BAR_CSS + '\n.sf-bar{')

# buildSfBar 함수 주입
if 'buildSfBar' not in html:
    html = html.replace('function renderCardUI()', SF_BAR_JS + '\nfunction renderCardUI()')

# renderCardUI 교체
html = re.sub(
    r'function renderCardUI\(\)\s*\{.*?document\.getElementById\(\'kv\'\)\.innerHTML\s*=\s*`[^`]*<div class="sf-bar">[^`]*`\s*;',
    PATCH_CARD_SF, html, flags=re.DOTALL)

# renderQuizUI 교체
html = re.sub(
    r'function renderQuizUI\(\)\s*\{.*?document\.getElementById\(\'qv\'\)\.innerHTML\s*=\s*`[^`]*<div class="sf-bar">[^`]*`\s*;',
    PATCH_QUIZ_SF, html, flags=re.DOTALL)

# ── K-Trivia 세트 선택 추가 ────────────────────────────────────────────────────

TRIVIA_SET_CSS = """
/* ─── TRIVIA SETS ─── */
#tv-sets-sel{padding:18px 14px}
.tv-set-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:14px}
.tv-set-btn{padding:14px 8px;border-radius:12px;border:2px solid var(--brd2);
  background:var(--surf2);cursor:pointer;text-align:center;transition:.15s;font-weight:700}
.tv-set-btn:hover{border-color:var(--a);background:var(--al)}
.tv-set-btn .tsn{font-size:1.1rem;font-weight:800;color:var(--tx)}
.tv-set-btn .tsq{font-size:.7rem;color:var(--tx3);margin-top:3px}
.tv-set-btn .tsc{font-size:.65rem;color:#16a34a;margin-top:2px;font-weight:700}
"""

TRIVIA_SET_JS = """
// ── TRIVIA SET SELECTOR ───────────────────────────────────────────────────────
const TV_SET_SIZE = 10;
let TV_SET_IDX = -1; // -1 = 전체

function showTvSets(cat) {
  TV_CAT = cat;
  const meta = TRIVIA_META[cat];
  const total = TRIVIA_DB[cat].length;
  const sets  = Math.ceil(total / TV_SET_SIZE);
  let btns = '';
  for (let s=0; s<sets; s++){
    const score = getTvSetScore(cat, s);
    btns += `<div class="tv-set-btn" onclick="startTriviaSet('${cat}',${s})" style="border-color:${meta.color}22">
      <div class="tsn">Set ${s+1}</div>
      <div class="tsq">Q${s*TV_SET_SIZE+1}–${Math.min((s+1)*TV_SET_SIZE,total)}</div>
      ${score ? `<div class="tsc">✓ ${score}</div>` : ''}
    </div>`;
  }
  btns += `<div class="tv-set-btn" onclick="startTriviaSet('${cat}',-1)" style="grid-column:1/-1">
    <div class="tsn">전체 · All (${total}문제)</div>
    <div class="tsq">랜덤 ${TV_SET_SIZE}문제</div>
  </div>`;
  document.getElementById('tv-cats').style.display = 'none';
  document.getElementById('tv-quiz').style.display = 'none';
  const ss = document.getElementById('tv-sets-sel');
  ss.style.display = 'block';
  ss.innerHTML = `
    <button class="tv-back" onclick="backToTvCats()">← 카테고리</button>
    <div style="display:flex;align-items:center;gap:10px;margin:12px 0 4px">
      <span style="font-size:2rem">${meta.icon||'🌟'}</span>
      <div>
        <div style="font-weight:800;font-size:1rem">${meta.label}</div>
        <div style="font-size:.75rem;color:var(--tx3)">${total}문제 · ${sets} Sets</div>
      </div>
    </div>
    <div class="tv-set-grid">${btns}</div>`;
}

function backToTvCats(){
  document.getElementById('tv-sets-sel').style.display='none';
  showTvCats();
}

function getTvSetScore(cat, s){
  try{ return localStorage.getItem('bwk_tv_'+cat+'_'+s)||''; }catch(e){return '';}
}

function startTriviaSet(cat, setIdx) {
  TV_CAT = cat; TV_SET_IDX = setIdx;
  const all = TRIVIA_DB[cat];
  if(setIdx < 0){
    TV_QS = shuffle(all).slice(0, TV_SET_SIZE);
  } else {
    const pool = all.slice(setIdx*TV_SET_SIZE, (setIdx+1)*TV_SET_SIZE);
    TV_QS = shuffle(pool);
  }
  TV_IDX=0; TV_SCORE=0; TV_ANS=null;
  const meta = TRIVIA_META[cat];
  const lb = document.getElementById('tv-cat-label');
  lb.textContent = meta.label + (setIdx>=0 ? ' · Set '+(setIdx+1) : '');
  lb.style.background = meta.color;
  document.getElementById('tv-sets-sel').style.display='none';
  document.getElementById('tv-cats').style.display='none';
  document.getElementById('tv-quiz').style.display='block';
  renderTvQ();
}
"""

# TV_CATS 카드: startTrivia → showTvSets
html = re.sub(r"onclick=\"startTrivia\('(\w+)'\)\"", r"onclick=\"showTvSets('\1')\"", html)

# startTrivia 함수를 showTvSets를 호출하도록 변경 (결과화면 "다시하기" 버튼도)
html = html.replace(
    "onclick=\"startTrivia(TV_CAT)\"",
    "onclick=\"showTvSets(TV_CAT)\"")

# tv-result에서 세트 저장
SAVE_TV_SCORE = """  // 세트 점수 저장
  if(TV_SET_IDX>=0){
    try{localStorage.setItem('bwk_tv_'+TV_CAT+'_'+TV_SET_IDX, TV_SCORE+'/'+TV_QS.length);}catch(e){}
  }
"""

html = re.sub(
    r'(function showTvResult\(\)\s*\{)',
    r'\1\n' + SAVE_TV_SCORE,
    html)

# tv 섹션에 tv-sets-sel div 추가
html = html.replace(
    '<div id="tv-cats">',
    '<div id="tv-sets-sel" style="display:none"></div>\n      <div id="tv-cats">')

# CSS 주입
if 'TRIVIA SETS' not in html:
    html = html.replace("/* ─── SET COMPLETE PULSE ─── */",
                        TRIVIA_SET_CSS + "\n/* ─── SET COMPLETE PULSE ─── */")

# JS 주입
if 'showTvSets' not in html:
    html = html.replace('function showTvCats(){',
                        TRIVIA_SET_JS + '\nfunction showTvCats(){')

# ── 저장 ────────────────────────────────────────────────────────────────────
out = BASE / "TOPIK_I_v4.html"
with open(out, "w", encoding="utf-8") as f:
    f.write(html)

size_kb = out.stat().st_size // 1024
print(f"\n✅ 저장 완료: {out}")
print(f"   파일 크기: {size_kb:,} KB")
print(f"   카테고리: {len(ALL_DATA)}개")
print(f"   총 단어:  {total_words:,}개")
