import re
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class SearchCriteria:
    """Search criteria for GitHub search"""

    query_type: str  # Query type: repo/code/user/topic
    main_topic: str  # Main topic
    sub_topics: List[str]  # Subtopics list
    language: str  # Programming language
    min_stars: int  # Minimum stars
    github_params: Dict  # GitHub search parameters
    original_query: str = ""  # Original query string
    repo_id: str = ""  # Specific repository ID or name


class QueryAnalyzer:
    """Query analyzer for GitHub searches"""

    # Response index constants
    BASIC_QUERY_INDEX = 0
    GITHUB_QUERY_INDEX = 1

    def __init__(self):
        self.valid_types = {
            "repo": ["repository", "project", "library", "framework", "tool"],
            "code": [
                "code",
                "snippet",
                "implementation",
                "function",
                "class",
                "algorithm",
            ],
            "user": ["user", "developer", "organization", "contributor", "maintainer"],
            "topic": ["topic", "category", "tag", "field", "area", "domain"],
        }

    def analyze_query(self, query: str, chatbot: List, llm_kwargs: Dict):
        """Analyze query intent"""
        from crazy_functions.crazy_utils import (
            request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency
            as request_gpt,
        )

        # 1. Basic query analysis
        type_prompt = f"""Please analyze this GitHub-related query and answer strictly in the following XML format:

Query: {query}

Instructions:
1. Your answer must use the XML tags shown below, with no text outside the tags
2. Select query type from: repo/code/user/topic
   - repo: for finding repositories, projects, frameworks, or libraries
   - code: for finding code snippets, function implementations, or algorithms
   - user: for finding users, developers, or organizations
   - topic: for finding topic, category, or domain related projects
3. Identify main topic and subtopics
4. Identify preferred programming language (if any)
5. Determine minimum stars (if applicable)

Required format:
<query_type>answer here</query_type>
<main_topic>answer here</main_topic>
<sub_topics>subtopic1, subtopic2, ...</sub_topics>
<language>answer here</language>
<min_stars>answer here</min_stars>

Example responses:

1. Repository query:
Query: "Find Python web frameworks with at least 1000 stars"
<query_type>repo</query_type>
<main_topic>web frameworks</main_topic>
<sub_topics>backend development, HTTP server, ORM</sub_topics>
<language>Python</language>
<min_stars>1000</min_stars>

2. Code query:
Query: "How to implement debounce function in JavaScript"
<query_type>code</query_type>
<main_topic>debounce function</main_topic>
<sub_topics>event handling, performance optimization, function throttling</sub_topics>
<language>JavaScript</language>
<min_stars>0</min_stars>"""

        # 2. Generate English search criteria
        github_prompt = f"""Optimize the following GitHub search query:

Query: {query}

Task: Convert the natural language query into an optimized GitHub search query.
Please use English, regardless of the language of the input query.

Available search fields and filters:
1. Basic fields:
   - in:name - Search in repository names
   - in:description - Search in repository descriptions
   - in:readme - Search in README files
   - in:topic - Search in topics
   - language:X - Filter by programming language
   - user:X - Repositories from a specific user
   - org:X - Repositories from a specific organization

2. Code search fields:
   - extension:X - Filter by file extension
   - path:X - Filter by path
   - filename:X - Filter by filename

3. Metric filters:
   - stars:>X - Has more than X stars
   - forks:>X - Has more than X forks
   - size:>X - Size greater than X KB
   - created:>YYYY-MM-DD - Created after a specific date
   - pushed:>YYYY-MM-DD - Updated after a specific date

4. Other filters:
   - is:public/private - Public or private repositories
   - archived:true/false - Archived or not archived
   - license:X - Specific license
   - topic:X - Contains specific topic tag

Examples:

1. Query: "Find Python machine learning libraries with at least 1000 stars"
<query>machine learning in:description language:python stars:>1000</query>

2. Query: "Recently updated React UI component libraries"
<query>UI components library in:readme in:description language:javascript topic:react pushed:>2023-01-01</query>

3. Query: "Open source projects developed by Facebook"
<query>org:facebook is:public</query>

4. Query: "Depth-first search implementation in JavaScript"
<query>depth first search in:file language:javascript</query>

Please analyze the query and answer using only the XML tag:
<query>Provide the optimized GitHub search query, using appropriate fields and operators</query>"""

        # 3. Generate Chinese search criteria
        chinese_github_prompt = f"""优化以下GitHub搜索查询:

查询: {query}

任务: 将自然语言查询转换为优化的GitHub搜索查询语句。
为了搜索中文内容，请提取原始查询的关键词并使用中文形式，同时保留GitHub特定的搜索语法为英文。

可用的搜索字段和过滤器:
1. 基本字段:
   - in:name - 在仓库名称中搜索
   - in:description - 在仓库描述中搜索
   - in:readme - 在README文件中搜索
   - in:topic - 在主题中搜索
   - language:X - 按编程语言筛选
   - user:X - 特定用户的仓库
   - org:X - 特定组织的仓库

2. 代码搜索字段:
   - extension:X - 按文件扩展名筛选
   - path:X - 按路径筛选
   - filename:X - 按文件名筛选

3. 指标过滤器:
   - stars:>X - 有超过X颗星
   - forks:>X - 有超过X个分支
   - size:>X - 大小超过X KB
   - created:>YYYY-MM-DD - 在特定日期后创建
   - pushed:>YYYY-MM-DD - 在特定日期后更新

4. 其他过滤器:
   - is:public/private - 公开或私有仓库
   - archived:true/false - 已归档或未归档
   - license:X - 特定许可证
   - topic:X - 含特定主题标签

示例:

1. 查询: "找有关机器学习的Python库，至少1000颗星"
<query>机器学习 in:description language:python stars:>1000</query>

2. 查询: "最近更新的React UI组件库"
<query>UI 组件库 in:readme in:description language:javascript topic:react pushed:>2023-01-01</query>

3. 查询: "微信小程序开发框架"
<query>微信小程序 开发框架 in:name in:description in:readme</query>

请分析查询并仅使用XML标签回答:
<query>提供优化的GitHub搜索查询，使用适当的字段和运算符，保留中文关键词</query>"""

        try:
            # Build prompt array
            prompts = [
                type_prompt,
                github_prompt,
                chinese_github_prompt,
            ]

            show_messages = [
                "Analyzing query type...",
                "Optimizing English GitHub search parameters...",
                "Optimizing Chinese GitHub search parameters...",
            ]

            sys_prompts = [
                "You are an expert in the GitHub ecosystem, skilled at analyzing GitHub-related queries.",
                "You are a GitHub search expert, specialized in converting natural language queries into optimized GitHub search queries in English.",
                "You are a GitHub search expert, skilled at processing queries and retaining Chinese keywords for searching.",
            ]

            # Use synchronous method to call LLM
            responses = yield from request_gpt(
                inputs_array=prompts,
                inputs_show_user_array=show_messages,
                llm_kwargs=llm_kwargs,
                chatbot=chatbot,
                history_array=[[] for _ in prompts],
                sys_prompt_array=sys_prompts,
                max_workers=3,
            )

            # Extract needed content from collected responses
            extracted_responses = []
            for i in range(len(prompts)):
                if (i * 2 + 1) < len(responses):
                    response = responses[i * 2 + 1]
                    if response is None:
                        raise Exception(f"Response {i} is None")
                    if not isinstance(response, str):
                        try:
                            response = str(response)
                        except:
                            raise Exception(f"Cannot convert response {i} to string")
                    extracted_responses.append(response)
                else:
                    raise Exception(f"Did not receive response {i + 1}")

            # Parse basic information
            query_type = self.extract_tag(
                extracted_responses[self.BASIC_QUERY_INDEX], "query_type"
            )
            if not query_type:
                print(
                    f"Debug - Failed to extract query_type. Response was: {extracted_responses[self.BASIC_QUERY_INDEX]}"
                )
                raise Exception("Cannot extract query_type tag content")
            query_type = query_type.lower()

            main_topic = self.extract_tag(
                extracted_responses[self.BASIC_QUERY_INDEX], "main_topic"
            )
            if not main_topic:
                print(f"Debug - Failed to extract main_topic. Using query as fallback.")
                main_topic = query

            query_type = self.normalize_query_type(query_type, query)

            # Extract subtopics
            sub_topics = []
            sub_topics_text = self.extract_tag(
                extracted_responses[self.BASIC_QUERY_INDEX], "sub_topics"
            )
            if sub_topics_text:
                sub_topics = [topic.strip() for topic in sub_topics_text.split(",")]

            # Extract language
            language = self.extract_tag(
                extracted_responses[self.BASIC_QUERY_INDEX], "language"
            )

            # Extract minimum stars
            min_stars = 0
            min_stars_text = self.extract_tag(
                extracted_responses[self.BASIC_QUERY_INDEX], "min_stars"
            )
            if min_stars_text and min_stars_text.isdigit():
                min_stars = int(min_stars_text)

            # Parse GitHub search parameters - English
            english_github_query = self.extract_tag(
                extracted_responses[self.GITHUB_QUERY_INDEX], "query"
            )

            # Parse GitHub search parameters - Chinese
            chinese_github_query = self.extract_tag(extracted_responses[2], "query")

            # Build GitHub parameters
            github_params = {
                "query": english_github_query,
                "chinese_query": chinese_github_query,
                "sort": "stars",  # Default sort by stars
                "order": "desc",  # Default descending order
                "per_page": 30,  # Default 30 items per page
                "page": 1,  # Default page 1
            }

            # Check if it's a specific repository query
            repo_id = ""
            if "repo:" in english_github_query or "repository:" in english_github_query:
                repo_match = re.search(
                    r"(repo|repository):([a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+)",
                    english_github_query,
                )
                if repo_match:
                    repo_id = repo_match.group(2)

            print(f"Debug - Extracted information:")
            print(f"Query type: {query_type}")
            print(f"Main topic: {main_topic}")
            print(f"Subtopics: {sub_topics}")
            print(f"Language: {language}")
            print(f"Minimum stars: {min_stars}")
            print(f"English GitHub parameters: {english_github_query}")
            print(f"Chinese GitHub parameters: {chinese_github_query}")
            print(f"Specific repository: {repo_id}")

            # Update returned SearchCriteria, including English and Chinese queries
            return SearchCriteria(
                query_type=query_type,
                main_topic=main_topic,
                sub_topics=sub_topics,
                language=language,
                min_stars=min_stars,
                github_params=github_params,
                original_query=query,
                repo_id=repo_id,
            )

        except Exception as e:
            raise Exception(f"Query analysis failed: {str(e)}")

    def normalize_query_type(self, query_type: str, query: str) -> str:
        """Normalize query type"""
        if query_type in ["repo", "code", "user", "topic"]:
            return query_type

        query_lower = query.lower()
        for type_name, keywords in self.valid_types.items():
            for keyword in keywords:
                if keyword in query_lower:
                    return type_name

        query_type_lower = query_type.lower()
        for type_name, keywords in self.valid_types.items():
            for keyword in keywords:
                if keyword in query_type_lower:
                    return type_name

        return "repo"  # Default return repo type

    def extract_tag(self, text: str, tag: str) -> str:
        """Extract tag content"""
        if not text:
            return ""

        # Standard XML format (handling multi-line and special characters)
        pattern = f"<{tag}>(.*?)</{tag}>"
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            content = match.group(1).strip()
            if content:
                return content

        # Alternative patterns
        patterns = [
            rf"<{tag}>\s*([\s\S]*?)\s*</{tag}>",  # Standard XML format
            rf"<{tag}>([\s\S]*?)(?:</{tag}>|$)",  # Unclosed tags
            rf"[{tag}]([\s\S]*?)[/{tag}]",  # Bracket format
            rf"{tag}:\s*(.*?)(?=\n\w|$)",  # Colon format
            rf"<{tag}>\s*(.*?)(?=<|$)",  # Partially closed
        ]

        # Try all patterns
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                content = match.group(1).strip()
                if content:  # Ensure extracted content is not empty
                    return content

        # If all patterns fail, return empty string
        return ""
