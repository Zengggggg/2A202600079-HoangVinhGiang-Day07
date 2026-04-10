# Báo Cáo Lab 7: Embedding & Vector Store

**Họ tên:** Hoàng Vĩnh Giang
**Nhóm:** F2-C401
**Ngày:** 10/04/2026

---

## 1. Warm-up (5 điểm)

### Cosine Similarity (Ex 1.1)

**High cosine similarity nghĩa là gì?**
> High cosine similarity (tiến gần về 1) nghĩa là hai vector có hướng gần như trùng nhau trong không gian vector, biểu thị sự tương đồng cao về mặt ngữ nghĩa hoặc ngữ cảnh của nội dung văn bản.

**Ví dụ HIGH similarity:**
- Sentence A: Mô hình ngôn ngữ lớn đang thay đổi cách chúng ta lập trình.

- Sentence B: AI tạo sinh đang tạo ra một cuộc cách mạng trong việc viết mã nguồn.

- Tại sao tương đồng: Cả hai câu đều đề cập đến cùng một chủ đề (AI/LLM) và tác động của nó đối với một hoạt động cụ thể (lập trình/coding).

**Ví dụ LOW similarity:**
- Sentence A: Hôm nay trời nắng rực rỡ tại Hà Nội.

- Sentence B: Thuật toán Q-Learning thuộc nhóm học tăng cường.

- Tại sao khác: Hai câu thuộc hai lĩnh vực hoàn toàn khác nhau (thời tiết và kỹ thuật máy tính), không có từ khóa hay ngữ cảnh chung.


**Tại sao cosine similarity được ưu tiên hơn Euclidean distance cho text embeddings?**
> Vì Cosine similarity chỉ đo góc giữa các vector mà không phụ thuộc vào độ dài (magnitude). Trong văn bản, một câu ngắn và một đoạn văn dài có thể cùng ý nghĩa, nhưng Euclidean distance sẽ coi chúng là "xa" nhau do sự khác biệt về số lượng từ (độ dài vector).

### Chunking Math (Ex 1.2)

**Document 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> $N = \lceil \frac{10000 - 50}{500 - 50} \rceil = \lceil \frac{9950}{450} \rceil = \lceil 22.11 \rceil$ = 23
> *Đáp án: 23*

**Nếu overlap tăng lên 100, chunk count thay đổi thế nào? Tại sao muốn overlap nhiều hơn?**
> $N = \lceil \frac{10000 - 100}{500 - 100} \rceil = \lceil \frac{9900}{400} \rceil = \lceil 24.75 \rceil$ = 25
> Đáp án: 25
---

## 2. Document Selection — Nhóm (10 điểm)

### Domain & Lý Do Chọn

**Domain:** Thương mại điện tử (E-commerce Platform) — Quy định hậu cần và chăm sóc khách hàng.

**Tại sao nhóm chọn domain này?**
> Nhóm chọn domain này vì các quy định về trả hàng, hoàn tiền và đồng kiểm trên các sàn thương mại điện tử thường có cấu trúc văn bản rõ ràng nhưng chứa nhiều điều kiện phức tạp (thời gian, loại mặt hàng, quy trình). Việc áp dụng Embedding và Vector Store vào tập dữ liệu này sẽ giúp xây dựng một hệ thống hỗ trợ khách hàng tự động, giúp người dùng tra cứu nhanh chóng các quyền lợi và nghĩa vụ mà không cần đọc qua các văn bản dài dòng.

### Data Inventory

| # | Tên tài liệu | Nguồn | Số ký tự | Metadata đã gán |
|---|--------------|-------|----------|-----------------|
| 1 | shopee_chinh_sach_tra_hang_hoan_tien.md | Shopee Help Center | 27,287  | source, filename |
| 2 | shopee_dong_kiem.md | Shopee Help Center | 9,948 | source, filename |
| 3 | shopee_huy_don_hoan_voucher.md | Shopee Help Center | 7,641 | source, filename |
| 4 | shopee_phuong_thuc_tra_hang.md | Shopee Help Center | 9,467 | source, filename |
| 5 | shopee_quy_dinh_chung_tra_hang.md | Shopee Help Center | 9,014 | source, filename |
| 6 | shopee_thoi_gian_hoan_tien.md | Shopee Help Center | 7,346 | source, filename |

### Metadata Schema

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho retrieval? |
|----------------|------|---------------|-------------------------------|
| source | string | data_phase_2/shopee_tra_hang.md | Xác định nguồn tài liệu, giúp trace và debug |
| filename | string | shopee_tra_hang.md | Hiển thị cho user, dễ hiểu hơn path |
| chunk_id | int | 3 | Phân biệt các đoạn nhỏ trong cùng 1 document |

---

## 3. Chunking Strategy — Cá nhân chọn, nhóm so sánh (15 điểm)

### Baseline Analysis

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Strategy | Chunk Count | Avg Length | Preserves Context? |
|-----------|----------|-------------|------------|-------------------|
| shopee_chinh_sach_tra_hang_hoan_tien.md | FixedSizeChunker (`fixed_size`) | 140 | 199.98 | Poor: Thường xuyên cắt ngang từ và làm mất tính liên kết giữa điều kiện và kết quả. |
| shopee_chinh_sach_tra_hang_hoan_tien.md | SentenceChunker (`by_sentences`) | 56 | 373.75 | Good: Giữ trọn vẹn ý nghĩa của từng câu đơn lẻ nhưng đôi khi gộp quá nhiều ý. |
| shopee_chinh_sach_tra_hang_hoan_tien.md | RecursiveChunker (`recursive`) | 179 | 116.37 | Excellent: Tách nhỏ theo cấu trúc Markdown giúp mỗi chunk là một quy định độc lập. |
| shopee_dong_kiem.md | FixedSizeChunker (`fixed_size`) | 54 | 199.13 | Poor: Cắt cứng theo số ký tự khiến các bảng biểu trong file bị hỏng định dạng. |
| shopee_dong_kiem.md | SentenceChunker (`by_sentences`) | 10 | 808.60 | Average: Chunk quá dài làm loãng vector embedding, gây khó khăn khi tìm ý chính. |
| shopee_dong_kiem.md | RecursiveChunker (`recursive`) | 64 | 125.39 | Excellent: Bảo toàn rất tốt các gạch đầu dòng (bullet points) về quy trình kiểm hàng. |
| shopee_phuong_thuc_tra_hang.md | FixedSizeChunker (`fixed_size`) | 51 | 197.13 | Poor: Ngữ cảnh bị rời rạc, khó xác định thông tin thuộc bước nào trong quy trình. |
| shopee_phuong_thuc_tra_hang.md | SentenceChunker (`by_sentences`) | 11 | 686.36 | Average: Giữ được các câu dài nhưng dễ lẫn lộn giữa các phương thức vận chuyển khác nhau. |
| shopee_phuong_thuc_tra_hang.md | RecursiveChunker (`recursive`) | 68 | 110.16 | Excellent: Phân tách rõ rệt từng bước thực hiện, cực kỳ tối ưu cho việc truy xuất quy trình. |


### Strategy Của Tôi

**Loại:** Custom Recursive strategy

**Mô tả cách hoạt động:**
> Chiến lược này sử dụng giải thuật chia để trị (divide and conquer) để phân rã văn bản dựa trên một danh sách các ký tự phân tách (separators) theo thứ tự ưu tiên giảm dần. Hệ thống sẽ cố gắng giữ các khối văn bản lớn nhất có thể trong phạm vi chunk_size, ưu tiên ngắt tại các vị trí như tiêu đề mục (##, ###), đoạn văn (\n\n), và các danh sách liệt kê (- ). Nếu một đoạn văn bản vẫn vượt quá kích thước cho phép sau khi đã thử mọi dấu hiệu phân tách, thuật toán sẽ thực hiện "hard split" theo độ dài ký tự để đảm bảo tính nhất quán của dữ liệu đầu ra.

**Tại sao tôi chọn strategy này cho domain nhóm?**
> *Domain về chính sách thương mại điện tử (Shopee) có đặc thù là chứa nhiều quy định dưới dạng danh sách điều kiện và các phân mục phân cấp rõ rệt. Strategy này cho phép khai thác cấu trúc Markdown của tài liệu để giữ nguyên vẹn ngữ cảnh của một điều khoản (không bị cắt ngang xương giữa chừng), giúp các vector embedding đại diện chính xác cho từng quy định cụ thể, từ đó nâng cao chất lượng tìm kiếm (retrieval) khi người dùng hỏi về các quy trình như hoàn tiền hay đồng kiểm.

**Code snippet (nếu custom):**
```python
class CustomChunker:
    """
    Recursively split text using separators in priority order.

    Default separator priority:
        ["\n\n", "\n", ". ", " ", ""]
    """

    DEFAULT_SEPARATORS = [
        "\n## ",   # Cắt theo Level 2 Header (Mục lớn)
        "\n### ",  # Cắt theo Level 3 Header (Mục nhỏ)
        "\n\n",    # Cắt theo đoạn văn
        "\n- ",    # Cắt theo các dòng bullet point (rất quan trọng cho chính sách)
        "\n",      # Cắt theo dòng đơn
        ". ",      # Cắt theo câu
        " ",       # Cắt theo từ
        ""         # Cắt theo ký tự (trường hợp cuối cùng)
    ]

    def __init__(self, separators: list[str] | None = None, chunk_size: int = 500) -> None:
        self.separators = self.DEFAULT_SEPARATORS if separators is None else list(separators)
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        # TODO: implement recursive splitting strategy
        if not text:
            return []

        return self._split(text, self.separators)

    def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
        # TODO: recursive helper used by RecursiveChunker.chunk
        if len(current_text) <= self.chunk_size:
            return [current_text.strip()]

        # nếu hết separator → hard split
        if not remaining_separators:
            return [
                current_text[i: i + self.chunk_size]
                for i in range(0, len(current_text), self.chunk_size)
            ]

        sep = remaining_separators[0]

        # split theo separator hiện tại
        if sep:
            parts = current_text.split(sep)
        else:
            # separator cuối: split từng ký tự
            parts = list(current_text)

        chunks = []
        buffer = ""

        for part in parts:
            piece = part if sep == "" else part + sep

            if len(buffer) + len(piece) <= self.chunk_size:
                buffer += piece
            else:
                if buffer:
                    chunks.extend(self._split(buffer.strip(), remaining_separators[1:]))
                buffer = piece

        if buffer:
            chunks.extend(self._split(buffer.strip(), remaining_separators[1:]))

        return chunks
```

### So Sánh: Strategy của tôi vs Baseline


| Tài liệu | Strategy | Chunk Count | Avg Length | Retrieval Quality? |
|-----------|----------|-------------|------------|--------------------|
| data/shopee_chinh_sach_tra_hang_hoan_tien.md | SentenceChunker (best baseline) | 56 | 374 | Trung bình - chunk thiếu context |
| data/shopee_chinh_sach_tra_hang_hoan_tien.md | Custom Recursive Chunking | 215 | 97.11 | Tốt - Truy vấn chính xác các đoạn chứa thông tin |


### So Sánh Với Thành Viên Khác

| Thành viên | Strategy | Retrieval Score (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Hoàng Vĩnh Giang | Custome Recursive Strategy | 8 | Chunking dựa theo cấu trúc của tài liệu, đảm bảo tính toàn vẹn của thông tin đoạn văn | với những đoạn dài chunk có thể vượt quá lượng ký tự cho phép của mô hình embedding |
| Nhữ Gia Bách | SemanticChunker | 8/10 | Chunk đúng chủ đề, score distribution rõ | Thiếu thông tin số liệu cụ thể khi chunk tách rời context |
| Trần Quang Quí | DocumentStructureChunker| 9/10 (5/5 relevant, avg score 0.628) | Chunk bám sát cấu trúc Q&A, context coherent, không bị cắt giữa điều khoản | Multi-aspect query (Q3) score thấp 0.59 vì định nghĩa và hướng dẫn nằm ở 2 chunk khác nhau |
| Đoàn Nam Sơn | Parent-Child Chunking| 9/10 (5/5 relevant, avg score 0.66) | Chunk hoạt động rất tốt, cắt đúng theo pattern Q&A, không bị cắt giữa điều khoản, rất phù hợp đối với các tài liệu có cấu trúc rõ ràng như. Tuy nhiên, với các tài liệu không có cấu trúc rõ ràng thì có thể không hiệu quả. |
| Vũ Đức Duy | Agentic Chunking (LLM gpt-4o-mini) | 9/10 (5/5 relevant, avg score 0.669) | Gom ngữ nghĩa cực sâu, tối ưu số lượng (chỉ tốn 54 chunks thay vì 209 chunks), không bị gãy đoạn văn. Điểm average score cao nhất. | Phải gọi API LLM tốn kém kinh phí, index siêu chậm, dễ dính lỗi parse JSON nếu document quá dài. |


**Strategy nào tốt nhất cho domain này? Tại sao?**
> Chiến lược Agentic Chunking kết hợp với DocumentStructureChunker là lựa chọn tốt nhất cho domain thương mại điện tử. Lý do là vì các tài liệu chính sách của Shopee có cấu trúc phân cấp phức tạp và mật độ thông tin cao; việc sử dụng LLM để gom nhóm ngữ nghĩa sâu giúp tối ưu hóa số lượng chunk mà không làm mất đi các mối liên kết logic giữa điều kiện và quyền lợi khách hàng. Điều này giúp hệ thống truy xuất chính xác các quy định cụ thể, tránh tình trạng thông tin bị cắt vụn hoặc loãng ngữ nghĩa như các phương pháp cắt dựa trên độ dài truyền thống.

---

## 4. My Approach — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi implement các phần chính trong package `src`.

### Chunking Functions

**`SentenceChunker.chunk`** — approach:
> SentenceChunker sử dụng regex để tách câu dựa trên các dấu kết thúc câu phổ biến như ., ?, !. Cụ thể, regex sẽ tìm các pattern có dấu câu theo sau bởi khoảng trắng và chữ cái viết hoa để xác định ranh giới giữa các câu.
Edge cases được xử lý bao gồm viết tắt (vd: “Dr.”, “e.g.”) và số thập phân để tránh split sai câu.

**`RecursiveChunker.chunk` / `_split`** — approach:
> RecursiveChunker hoạt động theo chiến lược chia nhỏ văn bản theo chiều đệ quy. Ban đầu nó cố gắng tách theo delimiter lớn (paragraph), nếu chunk vẫn vượt giới hạn thì tiếp tục chia nhỏ theo câu, và cuối cùng là theo từ nếu cần.
Base case là khi độ dài chunk nhỏ hơn hoặc bằng chunk_size, khi đó thuật toán dừng và trả về kết quả.

### EmbeddingStore

**`add_documents` + `search`** — approach:
> add_documents lưu trữ mỗi document dưới dạng một record gồm content và embedding vector được sinh từ OpenAI embedding model. Các vector này được lưu trong một list hoặc vector store nội bộ.
search tính toán similarity giữa query embedding và các document embedding bằng cosine similarity, sau đó trả về top-k kết quả có điểm cao nhất.

**`search_with_filter` + `delete_document`** — approach:
> search_with_filter thực hiện lọc metadata trước (pre-filtering) rồi mới tính similarity trên tập đã lọc để giảm chi phí tính toán.
delete_document hoạt động bằng cách loại bỏ document khỏi danh sách lưu trữ dựa trên id hoặc một thuộc tính định danh, sau đó cập nhật lại vector store.

### KnowledgeBaseAgent

**`answer`** — approach:
> Sử dụng kỹ thuật Context Injection bằng cách đưa các chunk văn bản có độ tương đồng cao nhất vào một khung prompt cố định. Prompt được chia làm 3 phần: (1) Role-setting để định nghĩa vai trò trợ lý, (2) Context constraint để giới hạn phạm vi trả lời trong dữ liệu đã cho và (3) Instruction yêu cầu trả lời "don't know" nếu thông tin thiếu hụt. Cách tiếp cận này giúp đảm bảo tính chính xác và tin cậy của câu trả lời đối với các chính sách phức tạp của Shopee.

### Test Results

```
====================================== test session starts ======================================= 
platform win32 -- Python 3.10.7, pytest-9.0.2, pluggy-1.6.0 -- C:\Users\admin\AppData\Local\Programs\Python\Python310\python.exe
cachedir: .pytest_cache
rootdir: D:\AI_IN_ACTION\LAB\Asg7\2A202600079-HoangVinhGiang-Day07
plugins: anyio-4.13.0, langsmith-0.7.26
collected 42 items                                                                                

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED       [  2%] 
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED                [  4%] 
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED         [  7%] 
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED          [  9%] 
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED               [ 11%] 
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED     [ 16%] 
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED      [ 19%] 
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED    [ 21%] 
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED                      [ 23%] 
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED      [ 26%] 
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED                 [ 28%] 
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED             [ 30%] 
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED                       [ 33%] 
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED  [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED  [ 42%] 
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED                      [ 45%] 
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED        [ 47%] 
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED          [ 50%] 
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED                [ 52%] 
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED     [ 54%] 
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED       [ 57%] 
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED        [ 61%] 
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED                 [ 64%] 
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED                [ 66%] 
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED           [ 69%] 
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED       [ 71%] 
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED  [ 73%] 
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED      [ 76%] 
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED            [ 78%] 
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED      [ 80%] 
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED [ 83%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED [ 85%] 
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED [ 92%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc
 PASSED [100%]

======================================= 42 passed in 0.11s ======================================= 
```

**Số tests pass:** 42 / 42

---

## 5. Similarity Predictions — Cá nhân (5 điểm)

| Pair | Sentence A                                                                                                                                  | Sentence B                                                                              | Dự đoán | Actual Score | Đúng? |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------- | ------- | ------------ | ----- |
| 1    | Người mua có bao nhiêu ngày để gửi yêu cầu trả hàng hoàn tiền đối với hàng Shopee Mall và hàng không thuộc Shopee Mall kể từ khi nhận hàng? | Thời gian tối đa để yêu cầu trả hàng sau khi nhận sản phẩm là bao lâu?                  | high    | 0.63         | Đúng     |
| 2    | Chính sách đổi trả áp dụng trong bao nhiêu ngày sau khi khách nhận hàng?                                                                    | Người dùng có thể yêu cầu hoàn tiền trong khoảng thời gian nào kể từ lúc nhận sản phẩm? | high    | 0.60         | Đúng     |
| 3    | Làm thế nào để liên hệ bộ phận hỗ trợ khách hàng khi gặp sự cố thanh toán?                                                                  | Người mua có thể đổi trả sản phẩm trong bao lâu kể từ ngày nhận hàng?                   | low     | 0.22         | Đúng     |
| 4    | Tôi quên mật khẩu tài khoản thì phải làm sao để khôi phục?                                                                                  | Các bước để lấy lại mật khẩu tài khoản bị quên là gì?                                   | high    | 0.65         | Đúng     |
| 5    | Phí vận chuyển có được hoàn lại khi trả hàng không?                                                                                         | Khi hoàn trả sản phẩm, người mua có được hoàn lại chi phí vận chuyển hay không?         | high    | 0.58         | Đúng     |


**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn nghĩa?**
> *Viết 2-3 câu:*

---

## 6. Results — Cá nhân (10 điểm)

Chạy 5 benchmark queries của nhóm trên implementation cá nhân của bạn trong package `src`. **5 queries phải trùng với các thành viên cùng nhóm.**

### Benchmark Queries & Gold Answers (nhóm thống nhất)

| # | Query | Gold Answer |
|---|-------|-------------|
| 1 | Tôi có bao nhiêu ngày để gửi yêu cầu trả hàng hoàn tiền? | 15 ngày kể từ lúc đơn hàng được cập nhật trạng thái Giao hàng thành công. |
| 2 | Tiền hoàn về ví ShopeePay mất bao lâu? | 24 giờ (với điều kiện Ví ShopeePay vẫn hoạt động bình thường). |
| 3 | Đồng kiểm là gì và tôi được làm gì khi đồng kiểm? | Kiểm tra ngoại quan và số lượng sản phẩm khi nhận hàng. Không được mở tem, dùng thử. |
| 4 | Nếu trả hàng theo hình thức tự sắp xếp, tôi có được hoàn phí vận chuyển không? | Có, Shopee hoàn lại trong 3-5 ngày làm việc (hoặc Shopee Xu với đơn ngoài Mall). |
| 5 | Mã giảm giá có được hoàn lại khi tôi trả hàng toàn bộ đơn không? | Có, mã giảm giá được hoàn nếu khiếu nại toàn bộ sản phẩm và được chấp nhận hoàn tiền. |

### Kết Quả Của Tôi
| # | Query | Top-1 Retrieved Chunk (tóm tắt) | Score | Relevant? | Agent Answer (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Tôi có bao nhiêu ngày để gửi yêu cầu trả hàng hoàn tiền? | source=data_phase_2/shopee_chinh_sach_tra_hang_hoan_tien.md | 0.577 | Yes | # Source: https://help.shopee.vn/portal/4/article/77251  # Xin chào, Shopee có thể giúp gì cho bạn?  ## CHÍNH SÁCH TRẢ H... |
| 2 | Tiền hoàn về ví ShopeePay mất bao lâu? | source=data_phase_2/shopee_chinh_sach_tra_hang_hoan_tien.md | 0.595 | Yes | Source: https://help.shopee.vn/portal/4/article/77251  # Xin chào, Shopee có thể giúp gì cho bạn?  ## CHÍNH SÁCH TRẢ H... |
| 3 | Đồng kiểm là gì và tôi được làm gì khi đồng kiểm? | source=data_phase_2/shopee_dong_kiem.md | 0.430 | Yes | Source: https://help.shopee.vn/portal/4/article/124982-%5BSHOPEE-%C4%90%E1%BB%92NG-KI%E1%BB%82M%5D-T%E1%BB%95ng-h%E1%B... |
| 4 | Nếu trả hàng theo hình thức tự sắp xếp, tôi có được hoàn phí vận chuyển không? | source=data_phase_2/shopee_phuong_thuc_tra_hang.md | 0.609 | Yes | # Source: https://help.shopee.vn/portal/4/article/189477-%5BTr%E1%BA%A3-h%C3%A0ng/-Ho%C3%A0n-ti%E1%BB%81n%5D-C%C3%A1c-ph... |
| 5 | Mã giảm giá có được hoàn lại khi tôi trả hàng toàn bộ đơn không? | source=data_phase_2/shopee_dong_kiem.md | 0.576 | Yes | Source: https://help.shopee.vn/portal/4/article/124982-%5BSHOPEE-%C4%90%E1%BB%92NG-KI%E1%BB%82M%5D-T%E1%BB%95ng-h%E1%B... |

**Bao nhiêu queries trả về chunk relevant trong top-3?** 5 / 5

---

## 7. What I Learned (5 điểm — Demo)

**Điều hay nhất tôi học được từ thành viên khác trong nhóm:**
> (Agentic chunking) Tôi học được cách áp dụng tư duy agentic trong việc xây dựng hệ thống, tức là chia nhỏ bài toán thành các bước như retrieval, reasoning và response thay vì xử lý một cách tuyến tính. Cách tiếp cận này giúp hệ thống linh hoạt hơn và dễ mở rộng khi cần thêm chức năng mới. Ngoài ra, agent có thể tự điều phối luồng xử lý nên cải thiện đáng kể chất lượng câu trả lời.

**Điều hay nhất tôi học được từ nhóm khác (qua demo):**
> Tôi ấn tượng với cách nhóm khác làm sạch dữ liệu trước khi đưa vào hệ thống bằng regex, đặc biệt là loại bỏ các ký tự đặc biệt, link và các phần không cần thiết. Việc này giúp dữ liệu đầu vào trở nên nhất quán và sạch hơn, từ đó cải thiện chất lượng embedding và kết quả retrieval. Đây là bước nhỏ nhưng ảnh hưởng lớn đến hiệu suất toàn hệ thống.

**Nếu làm lại, tôi sẽ thay đổi gì trong data strategy?**
> Nếu làm lại, tôi sẽ tập trung nhiều hơn vào chiến lược chia tài liệu bằng recursive chunking thay vì chỉ dùng các phương pháp đơn giản. Recursive giúp giữ được ngữ cảnh tốt hơn khi chia nhỏ văn bản, đặc biệt với các tài liệu dài và phức tạp. Điều này sẽ giúp cải thiện đáng kể chất lượng retrieval và độ chính xác của hệ thống RAG.

---

## Tự Đánh Giá

| Tiêu chí | Loại | Điểm tự đánh giá |
|----------|------|-------------------|
| Warm-up | Cá nhân | 5 / 5 |
| Document selection | Nhóm | 10 / 10 |
| Chunking strategy | Nhóm | 15 / 15 |
| My approach | Cá nhân | 10 / 10 |
| Similarity predictions | Cá nhân | 5 / 5 |
| Results | Cá nhân | 10 / 10 |
| Core implementation (tests) | Cá nhân | 30 / 30 |
| Demo | Nhóm | 5 / 5 |
| **Tổng** | | **90/ 100** |
