"""
Module Seed Data — Khởi tạo dữ liệu mẫu phong phú cho WordDuel.
Bao gồm 6 bộ từ vựng (120 từ chất lượng cao):
  1. Oxford 3000 — Từ Vựng Cốt Lõi (Core English)
  2. Công Nghệ & Lập Trình (Tech & Developer Duel)
  3. IELTS & Academic — Từ Vựng Học Thuật Cấp Cao
  4. Kinh Doanh & Công Sở (Business & Office English)
  5. Giao Tiếp & Đời Sống Hàng Ngày (Daily Conversation & Life)
  6. Du Lịch & Khám Phá Thế Giới (Travel & World Adventure)
"""
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.word import WordSet, Word


SEED_WORD_SETS: List[Dict[str, Any]] = [
    {
        "title": "Oxford 3000 — Từ Vựng Cốt Lõi",
        "description": "20 từ vựng tiếng Anh thông dụng và cốt lõi nhất theo khung chuẩn Oxford",
        "words": [
            {
                "term": "achieve",
                "definition": "Đạt được, hoàn thành mục tiêu",
                "example": "She worked hard to achieve her dream of becoming a doctor.",
            },
            {
                "term": "ancient",
                "definition": "Cổ xưa, lâu đời",
                "example": "The archaeologists discovered an ancient temple in the jungle.",
            },
            {
                "term": "benefit",
                "definition": "Lợi ích, mang lại lợi ích",
                "example": "Regular exercise brings great benefits to mental health.",
            },
            {
                "term": "challenge",
                "definition": "Thử thách, thách thức",
                "example": "Learning a new language is a demanding but rewarding challenge.",
            },
            {
                "term": "decade",
                "definition": "Thập kỷ (giai đoạn 10 năm)",
                "example": "Technology has advanced dramatically over the past decade.",
            },
            {
                "term": "emerge",
                "definition": "Xuất hiện, nổi lên",
                "example": "The sun began to emerge from behind the dark clouds.",
            },
            {
                "term": "future",
                "definition": "Tương lai",
                "example": "We should make wise investments for our future.",
            },
            {
                "term": "global",
                "definition": "Toàn cầu, trên toàn thế giới",
                "example": "Climate change is a pressing global problem.",
            },
            {
                "term": "impact",
                "definition": "Tác động, ảnh hưởng mạnh mẽ",
                "example": "Social media has a huge impact on teenager behavior.",
            },
            {
                "term": "journey",
                "definition": "Hành trình, chuyến đi",
                "example": "Life is a long journey filled with valuable lessons.",
            },
            {
                "term": "maintain",
                "definition": "Duy trì, bảo dưỡng",
                "example": "It is crucial to maintain good relationship with colleagues.",
            },
            {
                "term": "modern",
                "definition": "Hiện đại, tân tiến",
                "example": "The new hospital is equipped with modern medical devices.",
            },
            {
                "term": "obtain",
                "definition": "Đạt được, thu được",
                "example": "You must obtain permission before using this equipment.",
            },
            {
                "term": "potential",
                "definition": "Tiềm năng, khả năng phát triển",
                "example": "The young student showed great potential in mathematics.",
            },
            {
                "term": "provide",
                "definition": "Cung cấp, mang lại",
                "example": "The school library provides free textbooks for students.",
            },
            {
                "term": "reflect",
                "definition": "Phản chiếu, suy ngẫm",
                "example": "Take some time to reflect on your achievements this year.",
            },
            {
                "term": "secure",
                "definition": "An toàn, bảo đảm",
                "example": "Always keep your personal passwords secure and private.",
            },
            {
                "term": "unique",
                "definition": "Độc đáo, có một không hai",
                "example": "Each culture has its own unique traditions and customs.",
            },
            {
                "term": "visible",
                "definition": "Có thể nhìn thấy được, rõ ràng",
                "example": "The mountain summit was clearly visible in the morning light.",
            },
            {
                "term": "wonder",
                "definition": "Tự hỏi, điều kỳ diệu",
                "example": "I wonder what the weather will be like tomorrow.",
            },
        ],
    },
    {
        "title": "Công Nghệ & Lập Trình (Tech & Dev)",
        "description": "Từ vựng chuyên ngành Công nghệ thông tin, Lập trình và Khoa học máy tính",
        "words": [
            {
                "term": "algorithm",
                "definition": "Thuật toán",
                "example": "The search engine uses a sophisticated ranking algorithm.",
            },
            {
                "term": "backend",
                "definition": "Hệ thống xử lý phía máy chủ và cơ sở dữ liệu",
                "example": "Node.js and FastAPI are widely used for backend development.",
            },
            {
                "term": "frontend",
                "definition": "Giao diện người dùng phía máy khách",
                "example": "React is one of the most popular frontend libraries today.",
            },
            {
                "term": "database",
                "definition": "Cơ sở dữ liệu",
                "example": "PostgreSQL is a powerful relational database system.",
            },
            {
                "term": "debug",
                "definition": "Tìm và sửa lỗi phần mềm",
                "example": "He spent hours trying to debug the memory leak issue.",
            },
            {
                "term": "deploy",
                "definition": "Triển khai phần mềm lên máy chủ",
                "example": "We will deploy the new release to production this Friday.",
            },
            {
                "term": "framework",
                "definition": "Khung kiến trúc lập trình",
                "example": "Django is a high-level Python web framework.",
            },
            {
                "term": "function",
                "definition": "Hàm, chức năng lập trình",
                "example": "This helper function calculates the Euclidean distance between points.",
            },
            {
                "term": "interface",
                "definition": "Giao diện, cổng kết nối tương tác",
                "example": "The user interface must be clean, intuitive, and responsive.",
            },
            {
                "term": "latency",
                "definition": "Độ trễ mạng",
                "example": "Low network latency is critical for real-time multiplayer games.",
            },
            {
                "term": "memory",
                "definition": "Bộ nhớ máy tính",
                "example": "The program consumed too much memory and crashed.",
            },
            {
                "term": "network",
                "definition": "Mạng máy tính",
                "example": "A secure local network connects all office computers.",
            },
            {
                "term": "protocol",
                "definition": "Giao thức truyền thông",
                "example": "HTTP and WebSocket are essential web communication protocols.",
            },
            {
                "term": "query",
                "definition": "Truy vấn dữ liệu",
                "example": "Write an SQL query to retrieve active users from the database.",
            },
            {
                "term": "repository",
                "definition": "Kho lưu trữ mã nguồn",
                "example": "Please push your code commit to the GitHub repository.",
            },
            {
                "term": "server",
                "definition": "Máy chủ",
                "example": "The application server handles thousands of requests per second.",
            },
            {
                "term": "syntax",
                "definition": "Cú pháp mã nguồn",
                "example": "Check your code carefully for any syntax errors before compiling.",
            },
            {
                "term": "variable",
                "definition": "Biến số lưu trữ giá trị",
                "example": "Declare a variable using let or const in JavaScript.",
            },
            {
                "term": "websocket",
                "definition": "Kết nối hai chiều thời gian thực",
                "example": "WebSockets enable real-time messaging between client and server.",
            },
            {
                "term": "endpoint",
                "definition": "Điểm truy cập API",
                "example": "The user profile endpoint returns JSON formatted data.",
            },
        ],
    },
    {
        "title": "IELTS & Academic — Từ Vựng Học Thuật Cấp Cao",
        "description": "Từ vựng Band 7.0+ phục vụ nghiên cứu học thuật và bài thi IELTS/TOEFL",
        "words": [
            {
                "term": "anticipate",
                "definition": "Dự đoán, lường trước",
                "example": "Economists anticipate a gradual recovery in consumer spending.",
            },
            {
                "term": "coherent",
                "definition": "Mạch lạc, chặt chẽ, dễ hiểu",
                "example": "She presented a coherent argument that convinced the entire board.",
            },
            {
                "term": "fluctuate",
                "definition": "Dao động, biến động thất thường",
                "example": "Oil prices continue to fluctuate due to global supply tensions.",
            },
            {
                "term": "inherent",
                "definition": "Vốn có, cố hữu",
                "example": "Stress is an inherent part of working in emergency healthcare.",
            },
            {
                "term": "diminish",
                "definition": "Giảm bớt, suy giảm giá trị",
                "example": "Nothing could diminish her enthusiasm for the ambitious project.",
            },
            {
                "term": "scrutinize",
                "definition": "Xem xét kỹ lưỡng, soi xét",
                "example": "The auditor was instructed to scrutinize every financial invoice.",
            },
            {
                "term": "abundant",
                "definition": "Dồi dào, phong phú",
                "example": "The tropical region is blessed with abundant natural resources.",
            },
            {
                "term": "comprehensive",
                "definition": "Toàn diện, bao quát",
                "example": "The report provides a comprehensive overview of climate change risks.",
            },
            {
                "term": "feasible",
                "definition": "Khả thi, có thể thực hiện được",
                "example": "The proposed plan is both technically sound and financially feasible.",
            },
            {
                "term": "prerequisite",
                "definition": "Điều kiện tiên quyết",
                "example": "Fluency in English is an essential prerequisite for this international role.",
            },
            {
                "term": "arbitrary",
                "definition": "Tùy tiện, độc đoán",
                "example": "The manager was criticized for making arbitrary disciplinary decisions.",
            },
            {
                "term": "versatile",
                "definition": "Đa năng, linh hoạt",
                "example": "She is a versatile actress who excels in comedy and drama alike.",
            },
            {
                "term": "pragmatic",
                "definition": "Thực tế, thực dụng",
                "example": "We need a pragmatic approach to resolve this complex situation.",
            },
            {
                "term": "obsolete",
                "definition": "Lỗi thời, không còn sử dụng",
                "example": "Floppy disks became completely obsolete decades ago.",
            },
            {
                "term": "conspicuous",
                "definition": "Dễ thấy, nổi bật, đáng chú ý",
                "example": "His flashy yellow sports car was conspicuous in the quiet town.",
            },
            {
                "term": "jeopardize",
                "definition": "Gây nguy hiểm, làm tổn hại",
                "example": "Reckless driving will jeopardize your safety and the lives of others.",
            },
            {
                "term": "mitigate",
                "definition": "Làm dịu bớt, giảm nhẹ hậu quả",
                "example": "Planting more trees helps mitigate the negative effects of air pollution.",
            },
            {
                "term": "lucrative",
                "definition": "Sinh lợi cao, kiếm nhiều tiền",
                "example": "Entering the renewable energy sector proved to be a lucrative business.",
            },
            {
                "term": "pervasive",
                "definition": "Lan tỏa khắp nơi, phổ biến rộng rãi",
                "example": "Digital smartphones have a pervasive influence on contemporary life.",
            },
            {
                "term": "ubiquitous",
                "definition": "Có mặt khắp nơi, phổ biến mọi chỗ",
                "example": "Wi-Fi connectivity is now virtually ubiquitous in major cities.",
            },
        ],
    },
    {
        "title": "Kinh Doanh & Công Sở (Business & Office)",
        "description": "Từ vựng đàm phán, quản trị dự án, tài chính và giao tiếp công sở chuyên nghiệp",
        "words": [
            {
                "term": "negotiate",
                "definition": "Đàm phán, thương lượng",
                "example": "Both companies met to negotiate the terms of the merger.",
            },
            {
                "term": "contract",
                "definition": "Hợp đồng pháp lý",
                "example": "Please review the clauses carefully before signing the contract.",
            },
            {
                "term": "revenue",
                "definition": "Doanh thu",
                "example": "The enterprise reported a 20 percent increase in quarterly revenue.",
            },
            {
                "term": "deadline",
                "definition": "Hạn chót hoàn thành công việc",
                "example": "Our engineering team worked overtime to meet the project deadline.",
            },
            {
                "term": "milestone",
                "definition": "Cột mốc quan trọng của dự án",
                "example": "Reaching one million active users was a massive corporate milestone.",
            },
            {
                "term": "client",
                "definition": "Khách hàng đối tác",
                "example": "Always maintain open and transparent communication with every client.",
            },
            {
                "term": "colleague",
                "definition": "Đồng nghiệp làm cùng cơ quan",
                "example": "She collaborates effectively with her marketing colleagues.",
            },
            {
                "term": "agenda",
                "definition": "Chương trình nghị sự, nội dung cuộc họp",
                "example": "The meeting agenda was distributed to all participants this morning.",
            },
            {
                "term": "proposal",
                "definition": "Bản đề xuất kế hoạch hoặc dự án",
                "example": "The research team submitted a compelling grant proposal to investors.",
            },
            {
                "term": "budget",
                "definition": "Ngân sách chi tiêu",
                "example": "We must ensure that project expenditures remain strictly within budget.",
            },
            {
                "term": "investment",
                "definition": "Khoản đầu tư vốn",
                "example": "Sustainable green tech represents a wise long-term investment.",
            },
            {
                "term": "strategy",
                "definition": "Chiến lược kinh doanh",
                "example": "The company devised a bold digital marketing strategy for the quarter.",
            },
            {
                "term": "campaign",
                "definition": "Chiến dịch quảng bá tiếp thị",
                "example": "The promotional launch campaign attracted thousands of prospective buyers.",
            },
            {
                "term": "feedback",
                "definition": "Ý kiến phản hồi đánh giá",
                "example": "Constructive user feedback helps us continually refine our software product.",
            },
            {
                "term": "enterprise",
                "definition": "Doanh nghiệp, tập đoàn quy mô lớn",
                "example": "Cloud solutions help enterprise organizations scale operations rapidly.",
            },
            {
                "term": "stakeholder",
                "definition": "Bên liên quan, cổ đông hữu quan",
                "example": "All major stakeholders agreed to the proposed organizational restructuring.",
            },
            {
                "term": "dividend",
                "definition": "Cổ tức chi trả cho nhà đầu tư",
                "example": "Shareholders were delighted to receive higher cash dividends this fiscal year.",
            },
            {
                "term": "turnover",
                "definition": "Doanh số hoặc tỷ lệ luân chuyển nhân sự",
                "example": "The company achieved high annual turnover despite challenging economic conditions.",
            },
            {
                "term": "executive",
                "definition": "Giám đốc điều hành cấp cao",
                "example": "The chief executive delivered an inspiring keynote address to employees.",
            },
            {
                "term": "monopoly",
                "definition": "Thế độc quyền thị trường",
                "example": "The antitrust regulator investigated the tech conglomerate for anti-competitive monopoly.",
            },
        ],
    },
    {
        "title": "Giao Tiếp & Đời Sống Hàng Ngày",
        "description": "Tính từ, hành động và cảm xúc quen thuộc trong giao tiếp tiếng Anh đời sống",
        "words": [
            {
                "term": "delicious",
                "definition": "Thơm ngon tuyệt vời (về đồ ăn)",
                "example": "This homemade pasta sauce is absolutely delicious.",
            },
            {
                "term": "exhausted",
                "definition": "Kiệt sức, vô cùng mệt mỏi",
                "example": "After running the 42km marathon, she felt completely exhausted.",
            },
            {
                "term": "cheerful",
                "definition": "Vui vẻ, phấn khởi, tươi tắn",
                "example": "His cheerful smile instantly brightened the whole room.",
            },
            {
                "term": "gorgeous",
                "definition": "Lộng lẫy, cực kỳ xinh đẹp",
                "example": "The sunset over the tropical ocean was simply gorgeous.",
            },
            {
                "term": "stubborn",
                "definition": "Bướng bỉnh, cứng đầu",
                "example": "He is too stubborn to admit that he made a mistake.",
            },
            {
                "term": "generous",
                "definition": "Hào phóng, rộng lượng",
                "example": "The kind donor made a generous monetary contribution to the charity.",
            },
            {
                "term": "polite",
                "definition": "Lịch sự, nhã nhặn",
                "example": "It is polite to say thank you whenever someone assists you.",
            },
            {
                "term": "anxious",
                "definition": "Lo lắng, bồn chồn",
                "example": "Students often feel anxious before taking major university exams.",
            },
            {
                "term": "curious",
                "definition": "Tò mò, hiếu kỳ muốn khám phá",
                "example": "The curious child asked countless questions about astronomy.",
            },
            {
                "term": "convenient",
                "definition": "Tiện lợi, thuận tiện",
                "example": "The apartment is in a convenient location near the subway station.",
            },
            {
                "term": "reliable",
                "definition": "Đáng tin cậy",
                "example": "My vintage bicycle is still remarkably reliable after all these years.",
            },
            {
                "term": "hilarious",
                "definition": "Cực kỳ hài hước, gây cười nắc nẻ",
                "example": "The comedy movie had the entire theater audience in hilarious laughter.",
            },
            {
                "term": "awkward",
                "definition": "Gượng gạo, ngượng ngùng, lúng túng",
                "example": "There was an awkward silence when neither person knew what to say.",
            },
            {
                "term": "fragile",
                "definition": "Dễ vỡ, mỏng manh",
                "example": "Handle the glassware with extreme care because it is fragile.",
            },
            {
                "term": "cautious",
                "definition": "Thận trọng, cẩn thận",
                "example": "Drivers must be extra cautious when traveling on icy winter roads.",
            },
            {
                "term": "clumsy",
                "definition": "Vụng về, lóng ngóng",
                "example": "I felt clumsy when I accidentally knocked over the water glass.",
            },
            {
                "term": "sensible",
                "definition": "Hợp lý, khôn ngoan, biết suy nghĩ",
                "example": "Buying a modest fuel-efficient car was a sensible decision.",
            },
            {
                "term": "ambitious",
                "definition": "Tham vọng, có hoài bão lớn",
                "example": "The ambitious young entrepreneur plans to build a global startup.",
            },
            {
                "term": "punctual",
                "definition": "Đúng giờ, chuẩn giờ giấc",
                "example": "It is essential to be punctual for corporate job interviews.",
            },
            {
                "term": "thoughtful",
                "definition": "Chu đáo, ân cần, biết quan tâm",
                "example": "Sending flowers on her birthday was a remarkably thoughtful gesture.",
            },
        ],
    },
    {
        "title": "Du Lịch & Khám Phá Thế Giới",
        "description": "Từ vựng du lịch, sân bay, khách sạn, phong cảnh và khám phá các nền văn hóa",
        "words": [
            {
                "term": "destination",
                "definition": "Điểm đến du lịch",
                "example": "Da Nang is an increasingly popular vacation destination for international tourists.",
            },
            {
                "term": "passport",
                "definition": "Hộ chiếu xuất nhập cảnh",
                "example": "Always keep your international passport in a secure zipper pocket.",
            },
            {
                "term": "luggage",
                "definition": "Hành lý xách tay hoặc ký gửi",
                "example": "The airline staff helped passengers retrieve lost baggage and luggage.",
            },
            {
                "term": "itinerary",
                "definition": "Lịch trình chuyến đi chi tiết",
                "example": "Our travel guide outlined a thrilling five-day sightseeing itinerary.",
            },
            {
                "term": "boarding",
                "definition": "Lên máy bay hoặc tàu",
                "example": "Passengers should arrive at the designated boarding gate thirty minutes early.",
            },
            {
                "term": "souvenir",
                "definition": "Quà lưu niệm du lịch",
                "example": "She purchased a handmade ceramic bowl as a memorable souvenir.",
            },
            {
                "term": "landscape",
                "definition": "Phong cảnh thiên nhiên",
                "example": "The mountainous highland landscape was breathtakingly majestic.",
            },
            {
                "term": "excursion",
                "definition": "Chuyến tham quan dã ngoại ngắn ngày",
                "example": "We joined a guided afternoon boat excursion along the coastal islands.",
            },
            {
                "term": "accommodation",
                "definition": "Chỗ ở lưu trú (khách sạn, nhà nghỉ)",
                "example": "Our package tour includes luxury beachfront accommodation.",
            },
            {
                "term": "currency",
                "definition": "Tiền tệ quốc gia",
                "example": "You can exchange foreign currency at official airport exchange counters.",
            },
            {
                "term": "adventure",
                "definition": "Cuộc phiêu lưu kỳ thú",
                "example": "Trekking deep inside the rainforest was the greatest adventure of my life.",
            },
            {
                "term": "departure",
                "definition": "Giờ khởi hành, chuyến bay đi",
                "example": "Passengers waited in the airport departure lounge for final boarding calls.",
            },
            {
                "term": "arrival",
                "definition": "Giờ đến nơi, chuyến bay đến",
                "example": "Check the arrival monitor to find out which baggage carousel to wait at.",
            },
            {
                "term": "reservation",
                "definition": "Đặt phòng hoặc đặt chỗ trước",
                "example": "We made an advance dinner reservation at the rooftop restaurant.",
            },
            {
                "term": "landmark",
                "definition": "Thắng cảnh biểu tượng nổi tiếng",
                "example": "The Eiffel Tower is the most recognized architectural landmark in Paris.",
            },
            {
                "term": "breathtaking",
                "definition": "Đẹp đến nghẹt thở, ngoạn mục",
                "example": "The panoramic view from the summit mountain peak was breathtaking.",
            },
            {
                "term": "scenic",
                "definition": "Có phong cảnh thiên nhiên đẹp nên thơ",
                "example": "We enjoyed a relaxing drive along the scenic coastal highway.",
            },
            {
                "term": "voyage",
                "definition": "Chuyến hải trình dài ngày trên biển",
                "example": "The luxury cruise voyage lasted three magnificent weeks across the Mediterranean.",
            },
            {
                "term": "passenger",
                "definition": "Hành khách di chuyển",
                "example": "Flight attendants welcomed each arriving passenger with warm hospitality.",
            },
            {
                "term": "heritage",
                "definition": "Di sản văn hóa hoặc lịch sử",
                "example": "Hoi An ancient town is recognized as a UNESCO World Heritage site.",
            },
        ],
    },
]


def seed_words_data(db: Session, force: bool = False) -> int:
    """
    Thêm dữ liệu mẫu các bộ từ vào cơ sở dữ liệu.
    Nếu force=False: chỉ thêm những bộ từ chưa có (dựa theo title).
    Trả về số lượng từ đã thêm mới.
    """
    added_words_count = 0

    for set_data in SEED_WORD_SETS:
        existing_set = db.query(WordSet).filter(WordSet.title == set_data["title"]).first()
        if existing_set and not force:
            continue

        if not existing_set:
            new_set = WordSet(
                title=set_data["title"],
                description=set_data.get("description", ""),
                creator_id=None,
            )
            db.add(new_set)
            db.commit()
            db.refresh(new_set)
            target_set_id = new_set.id
        else:
            target_set_id = existing_set.id

        # Thêm các từ vựng vào bộ từ
        for w in set_data["words"]:
            # Tránh trùng lặp từ trong cùng bộ
            existing_word = (
                db.query(Word)
                .filter(Word.word_set_id == target_set_id, Word.term == w["term"].strip().lower())
                .first()
            )
            if not existing_word:
                new_word = Word(
                    word_set_id=target_set_id,
                    term=w["term"].strip().lower(),
                    definition=w["definition"].strip(),
                    example=w.get("example", "").strip(),
                )
                db.add(new_word)
                added_words_count += 1

        db.commit()

    return added_words_count


def run_seed_if_empty() -> None:
    """
    Ham duoc goi tu dong khi khoi chay app:
    Neu DB chua co bo tu nao, tu dong seed toan bo du lieu mau vao.
    """
    db = SessionLocal()
    try:
        current_sets_count = db.query(WordSet).count()
        if current_sets_count == 0:
            print("[Auto-Seed] Database is empty. Seeding initial vocabulary sets...")
            count = seed_words_data(db)
            print(f"[Auto-Seed] Successfully seeded {len(SEED_WORD_SETS)} word sets with {count} words!")
        else:
            print(f"[Auto-Seed] Database already contains {current_sets_count} word sets.")
    except Exception as e:
        print(f"[Auto-Seed] Error while seeding data: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("--- Starting manual seed script ---")
    session = SessionLocal()
    try:
        total = seed_words_data(session, force=False)
        print(f"Done! Successfully seeded {total} words into database.")
    finally:
        session.close()

