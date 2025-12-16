import re
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class SearchCriteria:
    """
    Search criteria for GitHub search operations.

    Attributes:
        query_type: Type of query (repo/code/user/topic)
        main_topic: Main search topic
        sub_topics: List of related subtopics
        language: Programming language filter
        min_stars: Minimum star count filter
        github_params: Dictionary of GitHub API parameters
        original_query: Original user query string
        repo_id: Specific repository identifier (owner/repo format)
    """

    query_type: str
    main_topic: str
    sub_topics: List[str]
    language: str
    min_stars: int
    github_params: Dict
    original_query: str = ""
    repo_id: str = ""


class QueryAnalyzer:
    """
    Analyzes user queries and converts them into structured GitHub search criteria.

    This class uses LLM to understand natural language queries and generate
    optimized GitHub search queries in both English and Chinese.
    """

    # Response index constants
    BASIC_QUERY_INDEX = 0
    GITHUB_QUERY_INDEX = 1

    def __init__(self):
        """Initialize the QueryAnalyzer with valid query type mappings."""
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
        """
        Analyze user query and generate structured search criteria.

        Args:
            query: Natural language query from user
            chatbot: Chatbot interface for displaying messages
            llm_kwargs: Keyword arguments for LLM configuration

        Returns:
            SearchCriteria object with parsed query information

        Raises:
            Exception: If query analysis fails or LLM response is invalid
        """
        from crazy_functions.crazy_utils import (
            request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency
            as request_gpt,
        )

        prompts = self._build_prompts(query)
        responses = yield from self._call_llm_parallel(
            prompts, chatbot, llm_kwargs
        )

        return self._parse_responses(responses, query)

    def _build_prompts(self, query: str) -> List[str]:
        """Build LLM prompts for query analysis."""
        type_prompt = self._build_type_prompt(query)
        github_prompt = self._build_github_prompt(query)
        chinese_prompt = self._build_chinese_prompt(query)

        return [type_prompt, github_prompt, chinese_prompt]

    def _build_type_prompt(self, query: str) -> str:
        """Build prompt for query type analysis."""
        return (
            "Please analyze this GitHub-related query and answer strictly in the "
            "following XML format:\n\n"
            f"Query: {query}\n\n"
            "Instructions:\n"
            "1. Your answer must use the XML tags shown below, with no text "
            "outside the tags\n"
            "2. Select query type from: repo/code/user/topic\n"
            "   - repo: for finding repositories, projects, frameworks, or libraries\n"
            "   - code: for finding code snippets, function implementations, or "
            "algorithms\n"
            "   - user: for finding users, developers, or organizations\n"
            "   - topic: for finding topic, category, or domain related projects\n"
            "3. Identify main topic and subtopics\n"
            "4. Identify preferred programming language (if any)\n"
            "5. Determine minimum stars (if applicable)\n\n"
            "Required format:\n"
            "<query_type>answer here</query_type>\n"
            "<main_topic>answer here</main_topic>\n"
            "<sub_topics>subtopic1, subtopic2, ...</sub_topics>\n"
            "<language>answer here</language>\n"
            "<min_stars>answer here</min_stars>\n\n"
            "Example responses:\n\n"
            "1. Repository query:\n"
            'Query: "Find Python web frameworks with at least 1000 stars"\n'
            "<query_type>repo</query_type>\n"
            "<main_topic>web frameworks</main_topic>\n"
            "<sub_topics>backend development, HTTP server, ORM</sub_topics>\n"
            "<language>Python</language>\n"
            "<min_stars>1000</min_stars>\n\n"
            "2. Code query:\n"
            'Query: "How to implement debounce function in JavaScript"\n'
            "<query_type>code</query_type>\n"
            "<main_topic>debounce function</main_topic>\n"
            "<sub_topics>event handling, performance optimization, function "
            "throttling</sub_topics>\n"
            "<language>JavaScript</language>\n"
            "<min_stars>0</min_stars>"
        )

    def _build_github_prompt(self, query: str) -> str:
        """Build prompt for English GitHub query optimization."""
        return (
            "Optimize the following GitHub search query:\n\n"
            f"Query: {query}\n\n"
            "Task: Convert the natural language query into an optimized GitHub "
            "search query.\n"
            "Please use English, regardless of the language of the input query.\n\n"
            "Available search fields and filters:\n"
            "1. Basic fields:\n"
            "   - in:name - Search in repository names\n"
            "   - in:description - Search in repository descriptions\n"
            "   - in:readme - Search in README files\n"
            "   - in:topic - Search in topics\n"
            "   - language:X - Filter by programming language\n"
            "   - user:X - Repositories from a specific user\n"
            "   - org:X - Repositories from a specific organization\n\n"
            "2. Code search fields:\n"
            "   - extension:X - Filter by file extension\n"
            "   - path:X - Filter by path\n"
            "   - filename:X - Filter by filename\n\n"
            "3. Metric filters:\n"
            "   - stars:>X - Has more than X stars\n"
            "   - forks:>X - Has more than X forks\n"
            "   - size:>X - Size greater than X KB\n"
            "   - created:>YYYY-MM-DD - Created after a specific date\n"
            "   - pushed:>YYYY-MM-DD - Updated after a specific date\n\n"
            "4. Other filters:\n"
            "   - is:public/private - Public or private repositories\n"
            "   - archived:true/false - Archived or not archived\n"
            "   - license:X - Specific license\n"
            "   - topic:X - Contains specific topic tag\n\n"
            "Examples:\n\n"
            '1. Query: "Find Python machine learning libraries with at least 1000 '
            'stars"\n'
            "<query>machine learning in:description language:python stars:>1000"
            "</query>\n\n"
            '2. Query: "Recently updated React UI component libraries"\n'
            "<query>UI components library in:readme in:description "
            "language:javascript topic:react pushed:>2023-01-01</query>\n\n"
            '3. Query: "Open source projects developed by Facebook"\n'
            "<query>org:facebook is:public</query>\n\n"
            '4. Query: "Depth-first search implementation in JavaScript"\n'
            "<query>depth first search in:file language:javascript</query>\n\n"
            "Please analyze the query and answer using only the XML tag:\n"
            "<query>Provide the optimized GitHub search query, using appropriate "
            "fields and operators</query>"
        )

    def _build_chinese_prompt(self, query: str) -> str:
        """Build prompt for Chinese GitHub query optimization."""
        return (
            "优化以下GitHub搜索查询:\n\n"
            f"查询: {query}\n\n"
            "任务: 将自然语言查询转换为优化的GitHub搜索查询语句。\n"
            "为了搜索中文内容，请提取原始查询的关键词并使用中文形式，同时保留GitHub"
            "特定的搜索语法为英文。\n\n"
            "可用的搜索字段和过滤器:\n"
            "1. 基本字段:\n"
            "   - in:name - 在仓库名称中搜索\n"
            "   - in:description - 在仓库描述中搜索\n"
            "   - in:readme - 在README文件中搜索\n"
            "   - in:topic - 在主题中搜索\n"
            "   - language:X - 按编程语言筛选\n"
            "   - user:X - 特定用户的仓库\n"
            "   - org:X - 特定组织的仓库\n\n"
            "2. 代码搜索字段:\n"
            "   - extension:X - 按文件扩展名筛选\n"
            "   - path:X - 按路径筛选\n"
            "   - filename:X - 按文件名筛选\n\n"
            "3. 指标过滤器:\n"
            "   - stars:>X - 有超过X颗星\n"
            "   - forks:>X - 有超过X个分支\n"
            "   - size:>X - 大小超过X KB\n"
            "   - created:>YYYY-MM-DD - 在特定日期后创建\n"
            "   - pushed:>YYYY-MM-DD - 在特定日期后更新\n\n"
            "4. 其他过滤器:\n"
            "   - is:public/private - 公开或私有仓库\n"
            "   - archived:true/false - 已归档或未归档\n"
            "   - license:X - 特定许可证\n"
            "   - topic:X - 含特定主题标签\n\n"
            "示例:\n\n"
            '1. 查询: "找有关机器学习的Python库，至少1000颗星"\n'
            "<query>机器学习 in:description language:python stars:>1000</query>\n\n"
            '2. 查询: "最近更新的React UI组件库"\n'
            "<query>UI 组件库 in:readme in:description language:javascript "
            "topic:react pushed:>2023-01-01</query>\n\n"
            '3. 查询: "微信小程序开发框架"\n'
            "<query>微信小程序 开发框架 in:name in:description in:readme</query>\n\n"
            "请分析查询并仅使用XML标签回答:\n"
            "<query>提供优化的GitHub搜索查询，使用适当的字段和运算符，保留中文关键词"
            "</query>"
        )

    def _call_llm_parallel(self, prompts, chatbot, llm_kwargs):
        """Call LLM with parallel processing for efficiency."""
        from crazy_functions.crazy_utils import (
            request_gpt_model_multi_threads_with_very_awesome_ui_and_high_efficiency
            as request_gpt,
        )

        show_messages = [
            "Analyzing query type...",
            "Optimizing English GitHub search parameters...",
            "Optimizing Chinese GitHub search parameters...",
        ]

        sys_prompts = [
            "You are an expert in the GitHub ecosystem, skilled at analyzing "
            "GitHub-related queries.",
            "You are a GitHub search expert, specialized in converting natural "
            "language queries into optimized GitHub search queries in English.",
            "You are a GitHub search expert, skilled at processing queries and "
            "retaining Chinese keywords for searching.",
        ]

        return (yield from request_gpt(
            inputs_array=prompts,
            inputs_show_user_array=show_messages,
            llm_kwargs=llm_kwargs,
            chatbot=chatbot,
            history_array=[[] for _ in prompts],
            sys_prompt_array=sys_prompts,
            max_workers=3,
        ))

    def _parse_responses(self, responses, query):
        """Parse LLM responses and build SearchCriteria object."""
        extracted_responses = self._extract_llm_responses(responses)

        query_type = self._parse_query_type(extracted_responses, query)
        main_topic = self._parse_main_topic(extracted_responses, query)
        sub_topics = self._parse_sub_topics(extracted_responses)
        language = self._parse_language(extracted_responses)
        min_stars = self._parse_min_stars(extracted_responses)
        
        english_query = self.extract_tag(
            extracted_responses[self.GITHUB_QUERY_INDEX], "query"
        )
        chinese_query = self.extract_tag(extracted_responses[2], "query")
        
        github_params = self._build_github_params(english_query, chinese_query)
        repo_id = self._extract_repo_id(english_query)

        self._log_debug_info(
            query_type, main_topic, sub_topics, language,
            min_stars, english_query, chinese_query, repo_id
        )

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

    def _extract_llm_responses(self, responses):
        """Extract LLM responses from the collected results."""
        extracted_responses = []
        for i in range(3):  # We always expect 3 responses
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
        return extracted_responses

    def _parse_query_type(self, responses, query):
        """Parse and normalize query type from LLM response."""
        query_type = self.extract_tag(responses[self.BASIC_QUERY_INDEX], "query_type")
        if not query_type:
            print(
                f"Debug - Failed to extract query_type. Response was: "
                f"{responses[self.BASIC_QUERY_INDEX]}"
            )
            raise Exception("Cannot extract query_type tag content")
        
        query_type = query_type.lower()
        return self.normalize_query_type(query_type, query)

    def _parse_main_topic(self, responses, query):
        """Parse main topic from LLM response."""
        main_topic = self.extract_tag(responses[self.BASIC_QUERY_INDEX], "main_topic")
        if not main_topic:
            print("Debug - Failed to extract main_topic. Using query as fallback.")
            return query
        return main_topic

    def _parse_sub_topics(self, responses):
        """Parse subtopics from LLM response."""
        sub_topics_text = self.extract_tag(
            responses[self.BASIC_QUERY_INDEX], "sub_topics"
        )
        if sub_topics_text:
            return [topic.strip() for topic in sub_topics_text.split(",")]
        return []

    def _parse_language(self, responses):
        """Parse programming language from LLM response."""
        return self.extract_tag(responses[self.BASIC_QUERY_INDEX], "language")

    def _parse_min_stars(self, responses):
        """Parse minimum stars from LLM response."""
        min_stars_text = self.extract_tag(
            responses[self.BASIC_QUERY_INDEX], "min_stars"
        )
        if min_stars_text and min_stars_text.isdigit():
            return int(min_stars_text)
        return 0

    def _build_github_params(self, english_query, chinese_query):
        """Build GitHub API parameters dictionary."""
        return {
            "query": english_query,
            "chinese_query": chinese_query,
            "sort": "stars",
            "order": "desc",
            "per_page": 30,
            "page": 1,
        }

    def _extract_repo_id(self, english_query):
        """Extract repository ID from GitHub query."""
        if "repo:" in english_query or "repository:" in english_query:
            repo_match = re.search(
                r"(repo|repository):([a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+)",
                english_query,
            )
            if repo_match:
                return repo_match.group(2)
        return ""

    def _log_debug_info(
        self, query_type, main_topic, sub_topics, language,
        min_stars, english_query, chinese_query, repo_id
    ):
        """Log debug information for development."""
        print("Debug - Extracted information:")
        print(f"Query type: {query_type}")
        print(f"Main topic: {main_topic}")
        print(f"Subtopics: {sub_topics}")
        print(f"Language: {language}")
        print(f"Minimum stars: {min_stars}")
        print(f"English GitHub parameters: {english_query}")
        print(f"Chinese GitHub parameters: {chinese_query}")
        print(f"Specific repository: {repo_id}")

    def normalize_query_type(self, query_type: str, query: str) -> str:
        """
        Normalize query type to one of the valid types.

        Args:
            query_type: Raw query type from LLM response
            query: Original user query for fallback analysis

        Returns:
            Normalized query type (repo/code/user/topic)
        """
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

        return "repo"

    def extract_tag(self, text: str, tag: str) -> str:
        """
        Extract content between XML tags using multiple pattern matching strategies.

        Args:
            text: Text containing XML tags
            tag: Name of the tag to extract

        Returns:
            Extracted content or empty string if not found
        """
        if not text:
            return ""

        pattern = f"<{tag}>(.*?)</{tag}>"
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            content = match.group(1).strip()
            if content:
                return content

        patterns = [
            rf"<{tag}>\s*([\s\S]*?)\s*</{tag}>",
            rf"<{tag}>([\s\S]*?)(?:</{tag}>|$)",
            rf"[{tag}]([\s\S]*?)[/{tag}]",
            rf"{tag}:\s*(.*?)(?=\n\w|$)",
            rf"<{tag}>\s*(.*?)(?=<|$)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                content = match.group(1).strip()
                if content:
                    return content

        return ""
