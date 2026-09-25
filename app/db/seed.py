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
import logging
from typing import Any
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.word import WordSet, Word

logger = logging.getLogger(__name__)


SEED_WORD_SETS: list[dict[str, Any]] = [
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
    {
  "title": "Giao tiếp cơ bản",
  "description": "Các từ vựng thông dụng dùng trong giao tiếp hằng ngày, chào hỏi và kết nối cơ bản",
  "words": [
    {
      "term": "greeting",
      "definition": "Lời chào hỏi",
      "example": "A friendly greeting is a great way to start a conversation."
    },
    {
      "term": "introduce",
      "definition": "Giới thiệu",
      "example": "Let me introduce my close friend to everyone."
    },
    {
      "term": "conversation",
      "definition": "Cuộc trò chuyện, đàm thoại",
      "example": "We had a long conversation about our future plans."
    },
    {
      "term": "apologize",
      "definition": "Xin lỗi",
      "example": "I apologize for being late to the meeting today."
    },
    {
      "term": "appreciation",
      "definition": "Sự trân trọng, cảm kích",
      "example": "She expressed her deep appreciation for their support."
    },
    {
      "term": "polite",
      "definition": "Lịch sự, nhã nhặn",
      "example": "It is always important to be polite to older people."
    },
    {
      "term": "suggestion",
      "definition": "Lời đề xuất, gợi ý",
      "example": "Do you have any suggestion for our lunch place?"
    },
    {
      "term": "opinion",
      "definition": "Quan điểm, ý kiến",
      "example": "In my opinion, learning English opens up many opportunities."
    },
    {
      "term": "agreement",
      "definition": "Sự đồng ý, thỏa thuận",
      "example": "We finally reached an agreement after a short discussion."
    },
    {
      "term": "disagree",
      "definition": "Không đồng ý, phản đối",
      "example": "I politely disagree with your point of view."
    },
    {
      "term": "compliment",
      "definition": "Lời khen ngợi",
      "example": "He gave her a nice compliment on her presentation."
    },
    {
      "term": "response",
      "definition": "Câu phản hồi, trả lời",
      "example": "I am waiting for his quick response to my email."
    },
    {
      "term": "assistance",
      "definition": "Sự trợ giúp, giúp đỡ",
      "example": "Please let me know if you need any assistance."
    },
    {
      "term": "pleasure",
      "definition": "Niềm vinh hạnh, sự hài lòng",
      "example": "It was a pleasure meeting you this afternoon."
    },
    {
      "term": "farewell",
      "definition": "Lời tạm biệt",
      "example": "They said a warm farewell before entering the station."
    },
    {
      "term": "pardon",
      "definition": "Thứ lỗi, xin lỗi (khi chưa nghe rõ)",
      "example": "Pardon me, could you repeat that sentence again?"
    },
    {
      "term": "mention",
      "definition": "Đề cập, nói đến",
      "example": "Don't mention it, I was happy to help you."
    },
    {
      "term": "welcome",
      "definition": "Chào đón, hoan nghênh",
      "example": "They gave a warm welcome to all new visitors."
    },
    {
      "term": "understand",
      "definition": "Hiểu, nắm bắt được",
      "example": "I completely understand what you are going through."
    },
    {
      "term": "explain",
      "definition": "Giải thích, làm rõ",
      "example": "Could you explain this concept a bit more clearly?"
    },
    {
      "term": "clarify",
      "definition": "Làm cho rõ ràng hơn",
      "example": "Let me clarify a few points before we proceed."
    },
    {
      "term": "interrupt",
      "definition": "Xen vào, ngắt lời",
      "example": "Sorry to interrupt, but you have an urgent phone call."
    },
    {
      "term": "expression",
      "definition": "Biểu cảm, cụm từ diễn đạt",
      "example": "\"Break a leg\" is an English expression meaning good luck."
    },
    {
      "term": "attitude",
      "definition": "Thái độ",
      "example": "A positive attitude makes daily communication much smoother."
    },
    {
      "term": "smalltalk",
      "definition": "Chuyện phiếm, trò chuyện xã giao",
      "example": "Making smalltalk with colleagues helps build good relationships."
    },
    {
      "term": "friendly",
      "definition": "Thân thiện, cởi mở",
      "example": "Our new neighbor is extremely friendly and helpful."
    },
    {
      "term": "honestly",
      "definition": "Thành thật mà nói",
      "example": "Honestly, I didn't expect the test to be so simple."
    },
    {
      "term": "probably",
      "definition": "Có lẽ, có thể",
      "example": "I will probably stay home and relax this weekend."
    },
    {
      "term": "definitely",
      "definition": "Chắc chắn, nhất định",
      "example": "I will definitely attend your birthday party tomorrow."
    },
    {
      "term": "certainly",
      "definition": "Dĩ nhiên, chắc chắn rồi",
      "example": "I can certainly help you carry those heavy books."
    },
    {
      "term": "advice",
      "definition": "Lời khuyên",
      "example": "My teacher gave me great advice regarding my career path."
    },
    {
      "term": "contact",
      "definition": "Liên lạc, kết nối",
      "example": "Please feel free to contact me whenever you need help."
    },
    {
      "term": "detail",
      "definition": "Chi tiết",
      "example": "Can you provide more detail about the upcoming event?"
    },
    {
      "term": "discussion",
      "definition": "Cuộc thảo luận",
      "example": "We had a productive discussion about the new project."
    },
    {
      "term": "feedback",
      "definition": "Ý kiến phản hồi",
      "example": "Constructive feedback helps us improve our work quality."
    },
    {
      "term": "invitation",
      "definition": "Lời mời",
      "example": "Thank you for sending me an invitation to your wedding."
    },
    {
      "term": "message",
      "definition": "Tin nhắn, thông điệp",
      "example": "I left a voice message on your phone an hour ago."
    },
    {
      "term": "notice",
      "definition": "Chú ý, nhận ra",
      "example": "Did you notice any changes in his behavior today?"
    },
    {
      "term": "permission",
      "definition": "Sự cho phép",
      "example": "You need permission from your boss before leaving early."
    },
    {
      "term": "question",
      "definition": "Câu hỏi, thắc mắc",
      "example": "If you have any question, please raise your hand."
    },
    {
      "term": "reason",
      "definition": "Lý do, nguyên nhân",
      "example": "The main reason for my call is to check on your health."
    },
    {
      "term": "request",
      "definition": "Lời yêu cầu, thỉnh cầu",
      "example": "The manager approved my request for a short leave."
    },
    {
      "term": "schedule",
      "definition": "Lịch trình, thời gian biểu",
      "example": "Let's check our schedule to find a good time to meet."
    },
    {
      "term": "share",
      "definition": "Chia sẻ",
      "example": "Would you mind sharing your experience with the group?"
    },
    {
      "term": "truth",
      "definition": "Sự thật, thực tế",
      "example": "It is always best to tell the truth in any situation."
    },
    {
      "term": "useful",
      "definition": "Hữu ích, bổ ích",
      "example": "This dictionary is very useful for English learners."
    },
    {
      "term": "wonderful",
      "definition": "Tuyệt vời, kỳ diệu",
      "example": "Have a wonderful day ahead with your family!"
    },
    {
      "term": "worry",
      "definition": "Lo lắng, bận tâm",
      "example": "Don't worry, everything will be completely fine."
    },
    {
      "term": "patience",
      "definition": "Sự kiên nhẫn",
      "example": "Thank you for your patience while we fix the issue."
    },
    {
      "term": "kindness",
      "definition": "Sự tốt bụng, lòng tốt",
      "example": "I will never forget your kindness during hard times."
    }
  ]
},
{
  "title": "Giao tiếp cơ bản (Đơn giản)",
  "description": "Các từ vựng tiếng Anh cơ bản nhất dùng trong giao tiếp, sinh hoạt và trò chuyện hằng ngày",
  "words": [
    {
      "term": "hello",
      "definition": "Xin chào",
      "example": "Hello, nice to meet you!"
    },
    {
      "term": "goodbye",
      "definition": "Tạm biệt",
      "example": "Goodbye, see you tomorrow!"
    },
    {
      "term": "thanks",
      "definition": "Cảm ơn",
      "example": "Thanks for your help today."
    },
    {
      "term": "please",
      "definition": "Làm ơn, xin vui lòng",
      "example": "Please give me a glass of water."
    },
    {
      "term": "sorry",
      "definition": "Xin lỗi",
      "example": "I am sorry for being late."
    },
    {
      "term": "yes",
      "definition": "Vâng, có, đồng ý",
      "example": "Yes, I would love to join."
    },
    {
      "term": "no",
      "definition": "Không",
      "example": "No, thank you, I am full."
    },
    {
      "term": "help",
      "definition": "Giúp đỡ",
      "example": "Can you help me with this box?"
    },
    {
      "term": "name",
      "definition": "Tên",
      "example": "My name is John."
    },
    {
      "term": "friend",
      "definition": "Bạn bè",
      "example": "She is my best friend."
    },
    {
      "term": "family",
      "definition": "Gia đình",
      "example": "I love my family very much."
    },
    {
      "term": "house",
      "definition": "Ngôi nhà",
      "example": "Their house has a beautiful garden."
    },
    {
      "term": "food",
      "definition": "Thức ăn, thực phẩm",
      "example": "Italian food is my favorite."
    },
    {
      "term": "water",
      "definition": "Nước",
      "example": "Drink plenty of water every day."
    },
    {
      "term": "time",
      "definition": "Thời gian, giờ",
      "example": "What time is the meeting?"
    },
    {
      "term": "day",
      "definition": "Ngày",
      "example": "Have a wonderful day!"
    },
    {
      "term": "night",
      "definition": "Ban đêm",
      "example": "Good night, sleep well!"
    },
    {
      "term": "work",
      "definition": "Làm việc, công việc",
      "example": "I go to work by bus every morning."
    },
    {
      "term": "school",
      "definition": "Trường học",
      "example": "The children are at school now."
    },
    {
      "term": "money",
      "definition": "Tiền bạc",
      "example": "How much money do we need?"
    },
    {
      "term": "happy",
      "definition": "Vui vẻ, hạnh phúc",
      "example": "She looks very happy today."
    },
    {
      "term": "sad",
      "definition": "Buồn bã",
      "example": "Why are you feeling sad?"
    },
    {
      "term": "good",
      "definition": "Tốt, hay",
      "example": "That sounds like a good idea."
    },
    {
      "term": "bad",
      "definition": "Tệ, dở",
      "example": "Bad weather kept us indoors."
    },
    {
      "term": "big",
      "definition": "Lớn, to",
      "example": "They live in a big city."
    },
    {
      "term": "small",
      "definition": "Nhỏ, bé",
      "example": "It is a small but cozy room."
    },
    {
      "term": "like",
      "definition": "Thích",
      "example": "I like listening to music."
    },
    {
      "term": "love",
      "definition": "Yêu, thương",
      "example": "Children love playing in the park."
    },
    {
      "term": "eat",
      "definition": "Ăn",
      "example": "Let's eat dinner together."
    },
    {
      "term": "drink",
      "definition": "Uống",
      "example": "Would you like to drink tea or coffee?"
    },
    {
      "term": "sleep",
      "definition": "Ngủ",
      "example": "I need to sleep eight hours every night."
    },
    {
      "term": "go",
      "definition": "Đi",
      "example": "We plan to go to the beach this weekend."
    },
    {
      "term": "come",
      "definition": "Đến, tới",
      "example": "Please come in and sit down."
    },
    {
      "term": "see",
      "definition": "Nhìn, thấy",
      "example": "See you again next week!"
    },
    {
      "term": "hear",
      "definition": "Nghe thấy",
      "example": "Can you hear that noise outside?"
    },
    {
      "term": "speak",
      "definition": "Nói",
      "example": "He can speak English very fluently."
    },
    {
      "term": "listen",
      "definition": "Lắng nghe",
      "example": "Listen carefully to the instructions."
    },
    {
      "term": "read",
      "definition": "Đọc",
      "example": "I like to read books before bed."
    },
    {
      "term": "write",
      "definition": "Viết",
      "example": "Please write your name here."
    },
    {
      "term": "buy",
      "definition": "Mua",
      "example": "I need to buy some fresh vegetables."
    },
    {
      "term": "pay",
      "definition": "Thanh toán, trả tiền",
      "example": "Can I pay with credit card?"
    },
    {
      "term": "ask",
      "definition": "Hỏi",
      "example": "Feel free to ask any question."
    },
    {
      "term": "answer",
      "definition": "Trả lời",
      "example": "She gave a quick answer."
    },
    {
      "term": "know",
      "definition": "Biết, hiểu",
      "example": "I know the answer to this question."
    },
    {
      "term": "think",
      "definition": "Nghĩ, suy nghĩ",
      "example": "I think it will rain today."
    },
    {
      "term": "want",
      "definition": "Muốn",
      "example": "Do you want a cup of coffee?"
    },
    {
      "term": "need",
      "definition": "Cần",
      "example": "I need your help with this work."
    },
    {
      "term": "today",
      "definition": "Hôm nay",
      "example": "Today is a sunny day."
    },
    {
      "term": "tomorrow",
      "definition": "Ngày mai",
      "example": "See you tomorrow at school."
    },
    {
      "term": "yesterday",
      "definition": "Hôm qua",
      "example": "We visited our grandparents yesterday."
    }
  ]
},
{
  "title": "Thanh Trường",
  "description": "Các từ vựng giao tiếp thông dụng trích xuất từ tệp 1.xlsx",
  "words": [
    {
      "term": "accept",
      "definition": "to say yes to something that is offered",
      "example": "She accepted the job offer."
    },
    {
      "term": "afraid",
      "definition": "feeling fear",
      "example": "I am afraid of dogs."
    },
    {
      "term": "agree",
      "definition": "to have the same opinion as someone",
      "example": "I agree with you."
    },
    {
      "term": "arrive",
      "definition": "to reach a place",
      "example": "We arrived at the station at six."
    },
    {
      "term": "borrow",
      "definition": "to take and use something and return it later",
      "example": "Can I borrow your pen?"
    },
    {
      "term": "break",
      "definition": "to damage something so that it does not work",
      "example": "Be careful not to break the glass."
    },
    {
      "term": "bring",
      "definition": "to take something with you to a place",
      "example": "Please bring your book tomorrow."
    },
    {
      "term": "build",
      "definition": "to make something by putting parts together",
      "example": "They are building a new house."
    },
    {
      "term": "busy",
      "definition": "having a lot to do",
      "example": "I am busy this afternoon."
    },
    {
      "term": "careful",
      "definition": "giving attention to avoid danger or mistakes",
      "example": "Be careful when you cross the road."
    },
    {
      "term": "carry",
      "definition": "to hold or move something from one place to another",
      "example": "She carried the box upstairs."
    },
    {
      "term": "cheap",
      "definition": "costing little money",
      "example": "This restaurant is cheap and good."
    },
    {
      "term": "choose",
      "definition": "to decide which person or thing you want",
      "example": "You can choose any color."
    },
    {
      "term": "clean",
      "definition": "not dirty",
      "example": "My room is clean now."
    },
    {
      "term": "clearly",
      "definition": "in a way that is easy to understand or see",
      "example": "Please speak clearly."
    },
    {
      "term": "climb",
      "definition": "to move up something using your hands and feet",
      "example": "We climbed the mountain last weekend."
    },
    {
      "term": "collect",
      "definition": "to get things of the same type as a hobby",
      "example": "He collects stamps."
    },
    {
      "term": "comfortable",
      "definition": "pleasant and not causing pain or difficulty",
      "example": "These shoes are very comfortable."
    },
    {
      "term": "continue",
      "definition": "to keep doing something",
      "example": "Please continue reading."
    },
    {
      "term": "corner",
      "definition": "the place where two streets or lines meet",
      "example": "The bank is on the corner."
    },
    {
      "term": "decide",
      "definition": "to choose something after thinking about it",
      "example": "We decided to stay at home."
    },
    {
      "term": "delicious",
      "definition": "having a very good taste",
      "example": "The cake was delicious."
    },
    {
      "term": "different",
      "definition": "not the same",
      "example": "My new school is different from my old one."
    },
    {
      "term": "difficult",
      "definition": "not easy to do or understand",
      "example": "This question is difficult."
    },
    {
      "term": "early",
      "definition": "before the usual or expected time",
      "example": "I got up early today."
    },
    {
      "term": "enough",
      "definition": "as much as is needed",
      "example": "We have enough food for everyone."
    },
    {
      "term": "especially",
      "definition": "more than usual or more than others",
      "example": "I like fruit, especially oranges."
    },
    {
      "term": "excited",
      "definition": "very happy and interested about something",
      "example": "The children are excited about the trip."
    },
    {
      "term": "expensive",
      "definition": "costing a lot of money",
      "example": "That phone is too expensive for me."
    },
    {
      "term": "famous",
      "definition": "known by many people",
      "example": "Paris is famous for the Eiffel Tower."
    },
    {
      "term": "finish",
      "definition": "to complete something",
      "example": "I need to finish my homework."
    },
    {
      "term": "follow",
      "definition": "to go after someone or something",
      "example": "Follow me, please."
    },
    {
      "term": "forget",
      "definition": "to not remember something",
      "example": "Don't forget your keys."
    },
    {
      "term": "friendly",
      "definition": "kind and pleasant to other people",
      "example": "Our new teacher is very friendly."
    },
    {
      "term": "future",
      "definition": "the time after now",
      "example": "I want to travel in the future."
    },
    {
      "term": "happen",
      "definition": "to take place",
      "example": "What happened yesterday?"
    },
    {
      "term": "healthy",
      "definition": "good for your health",
      "example": "Eating vegetables is healthy."
    },
    {
      "term": "helpful",
      "definition": "useful or willing to help",
      "example": "The hotel staff were very helpful."
    },
    {
      "term": "important",
      "definition": "having a lot of value or meaning",
      "example": "Sleep is important for your health."
    },
    {
      "term": "invite",
      "definition": "to ask someone to come to a place or event",
      "example": "I invited Tom to my party."
    },
    {
      "term": "journey",
      "definition": "an act of traveling from one place to another",
      "example": "The journey took three hours."
    },
    {
      "term": "kind",
      "definition": "friendly and caring",
      "example": "She is very kind to everyone."
    },
    {
      "term": "laugh",
      "definition": "to make a happy sound when something is funny",
      "example": "We laughed at his joke."
    },
    {
      "term": "learn",
      "definition": "to get knowledge or a skill",
      "example": "I am learning English."
    },
    {
      "term": "leave",
      "definition": "to go away from a place",
      "example": "We leave home at seven."
    },
    {
      "term": "lend",
      "definition": "to give something to someone for a short time",
      "example": "Can you lend me some money?"
    },
    {
      "term": "lucky",
      "definition": "having good things happen by chance",
      "example": "I was lucky to find my lost phone."
    },
    {
      "term": "message",
      "definition": "a piece of information sent to someone",
      "example": "I sent you a message."
    },
    {
      "term": "mistake",
      "definition": "something that you do wrong",
      "example": "I made a mistake in my homework."
    },
    {
      "term": "modern",
      "definition": "new and using the latest ideas or technology",
      "example": "They live in a modern apartment."
    },
    {
      "term": "necessary",
      "definition": "needed for a particular purpose",
      "example": "A passport is necessary for the trip."
    },
    {
      "term": "noisy",
      "definition": "making a lot of sound",
      "example": "The street is very noisy."
    },
    {
      "term": "notice",
      "definition": "to see or become aware of something",
      "example": "Did you notice the sign?"
    },
    {
      "term": "offer",
      "definition": "to ask someone if they would like something",
      "example": "He offered me a cup of coffee."
    },
    {
      "term": "opinion",
      "definition": "what you think about something",
      "example": "What's your opinion about this movie?"
    },
    {
      "term": "outside",
      "definition": "not inside a building or place",
      "example": "The children are playing outside."
    },
    {
      "term": "perhaps",
      "definition": "possibly; maybe",
      "example": "Perhaps we can meet tomorrow."
    },
    {
      "term": "popular",
      "definition": "liked or enjoyed by many people",
      "example": "Football is popular in many countries."
    },
    {
      "term": "prepare",
      "definition": "to get ready for something",
      "example": "I need to prepare for the exam."
    },
    {
      "term": "promise",
      "definition": "to say that you will certainly do something",
      "example": "I promise to call you tonight."
    },
    {
      "term": "quiet",
      "definition": "with very little noise",
      "example": "The library is quiet."
    },
    {
      "term": "receive",
      "definition": "to get something that someone sends or gives you",
      "example": "I received a letter yesterday."
    },
    {
      "term": "remember",
      "definition": "to keep something in your mind and not forget it",
      "example": "Remember to lock the door."
    },
    {
      "term": "repair",
      "definition": "to fix something that is broken",
      "example": "He repaired my bike."
    },
    {
      "term": "return",
      "definition": "to go or come back to a place",
      "example": "I will return home on Sunday."
    },
    {
      "term": "safe",
      "definition": "not in danger",
      "example": "This is a safe place to swim."
    },
    {
      "term": "save",
      "definition": "to keep money instead of spending it",
      "example": "I am saving money for a new laptop."
    },
    {
      "term": "seem",
      "definition": "to appear to be true",
      "example": "You seem tired today."
    },
    {
      "term": "share",
      "definition": "to use or have something together with another person",
      "example": "We share the same office."
    },
    {
      "term": "similar",
      "definition": "almost the same",
      "example": "The two houses are very similar."
    },
    {
      "term": "simple",
      "definition": "easy to understand or do",
      "example": "The instructions are simple."
    },
    {
      "term": "single",
      "definition": "not married",
      "example": "He is single."
    },
    {
      "term": "special",
      "definition": "different from usual in a good way",
      "example": "Today is a special day."
    },
    {
      "term": "spend",
      "definition": "to use money to buy something",
      "example": "I spent $20 on a book."
    },
    {
      "term": "stay",
      "definition": "to remain in a place for a period of time",
      "example": "We stayed at a hotel."
    },
    {
      "term": "strange",
      "definition": "unusual or surprising",
      "example": "I heard a strange noise."
    },
    {
      "term": "suddenly",
      "definition": "quickly and unexpectedly",
      "example": "Suddenly, the lights went out."
    },
    {
      "term": "suggest",
      "definition": "to give an idea about what someone should do",
      "example": "I suggest taking a taxi."
    },
    {
      "term": "together",
      "definition": "with each other",
      "example": "Let's work together."
    },
    {
      "term": "traffic",
      "definition": "the cars and other vehicles on the roads",
      "example": "There was a lot of traffic this morning."
    },
    {
      "term": "treat",
      "definition": "to behave toward someone in a particular way",
      "example": "She treats everyone with respect."
    },
    {
      "term": "useful",
      "definition": "helpful for a particular purpose",
      "example": "This dictionary is very useful."
    },
    {
      "term": "usual",
      "definition": "normal or common",
      "example": "I had my usual breakfast."
    },
    {
      "term": "visit",
      "definition": "to go to a person or place for a short time",
      "example": "We visited our grandparents."
    },
    {
      "term": "wait",
      "definition": "to stay until someone or something arrives",
      "example": "Please wait for me."
    },
    {
      "term": "weather",
      "definition": "the condition of the air outside at a particular time",
      "example": "The weather is sunny today."
    },
    {
      "term": "whole",
      "definition": "complete; all of something",
      "example": "I ate the whole cake."
    },
    {
      "term": "wonderful",
      "definition": "very good and enjoyable",
      "example": "We had a wonderful holiday."
    },
    {
      "term": "worried",
      "definition": "thinking about problems or being afraid of something",
      "example": "She is worried about the exam."
    },
    {
      "term": "advice",
      "definition": "an opinion about what someone should do",
      "example": "My teacher gave me some good advice."
    },
    {
      "term": "answer",
      "definition": "something you say or write in response to a question",
      "example": "I know the answer."
    },
    {
      "term": "appointment",
      "definition": "an arrangement to meet someone at a particular time",
      "example": "I have a doctor's appointment at ten."
    },
    {
      "term": "business",
      "definition": "work involving buying and selling goods or services",
      "example": "She runs a small business."
    },
    {
      "term": "customer",
      "definition": "a person who buys something",
      "example": "The customer paid by card."
    },
    {
      "term": "direction",
      "definition": "the way to go to a place",
      "example": "Can you tell me the direction to the station?"
    },
    {
      "term": "experience",
      "definition": "knowledge or skill gained from doing something",
      "example": "I have experience in ship design."
    },
    {
      "term": "information",
      "definition": "facts or details about something",
      "example": "Can you give me more information?"
    },
    {
      "term": "language",
      "definition": "a system of words used for communication",
      "example": "English is an international language."
    },
    {
      "term": "project",
      "definition": "a planned piece of work with a particular purpose",
      "example": "We are working on a new project."
    },
    {
      "term": "reason",
      "definition": "a cause or explanation for something",
      "example": "What's the reason for the delay?"
    },
    {
      "term": "result",
      "definition": "something that happens because of an action or event",
      "example": "The result was better than expected."
    }
  ]
}
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
    Ensure all built-in sample sets exist without replacing user data.
    """
    db = SessionLocal()
    try:
        current_sets_count = db.query(WordSet).count()
        count = seed_words_data(db, force=False)
        logger.info(
            "Seed check complete (existing sets: %s, sample sets: %s, words added: %s)",
            current_sets_count,
            len(SEED_WORD_SETS),
            count,
        )
    except Exception:
        db.rollback()
        logger.exception("Failed to seed initial vocabulary")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    session = SessionLocal()
    try:
        total = seed_words_data(session, force=False)
        logger.info("Seeded %s words into database", total)
    finally:
        session.close()
