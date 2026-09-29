import streamlit as st
import requests
from datetime import datetime

st.set_page_config(
    page_title="GitHub Profile Analyzer",
    page_icon="🐙",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .main {
        padding-top: 2rem;
    }

    .hero {
        text-align: center;
        padding: 30px 10px 20px 10px;
    }

    .hero h1 {
        font-size: 42px;
        margin-bottom: 5px;
    }

    .hero p {
        font-size: 18px;
        color: #888;
    }

    .profile-card {
        padding: 25px;
        border-radius: 15px;
        border: 1px solid rgba(128,128,128,0.25);
        margin-bottom: 20px;
    }

    .stat-card {
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        border: 1px solid rgba(128,128,128,0.25);
    }

    .stat-number {
        font-size: 28px;
        font-weight: bold;
    }

    .stat-label {
        color: #888;
        font-size: 14px;
    }

    .section-title {
        font-size: 25px;
        font-weight: bold;
        margin-top: 35px;
        margin-bottom: 15px;
    }

    .repo-card {
        padding: 18px;
        border-radius: 12px;
        border: 1px solid rgba(128,128,128,0.25);
        margin-bottom: 12px;
    }

    .footer {
        text-align: center;
        color: #888;
        margin-top: 50px;
        padding: 20px;
    }
</style>
""", unsafe_allow_html=True)


def get_username(value):

    value = value.strip().rstrip("/")

    if "github.com/" in value:
        value = value.split("github.com/")[-1]

    return value.split("/")[0]


def github_request(url):

    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "GitHub-Profile-Analyzer"
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=15
    )

    response.raise_for_status()

    return response.json()


def get_profile(username):

    return github_request(
        f"https://api.github.com/users/{username}"
    )


def get_repositories(username):

    return github_request(
        f"https://api.github.com/users/{username}/repos"
        f"?per_page=100&sort=updated"
    )


def get_readme(username, repo):

    url = (
        f"https://api.github.com/repos/"
        f"{username}/{repo}/readme"
    )

    headers = {
        "Accept": "application/vnd.github.raw+json",
        "User-Agent": "GitHub-Profile-Analyzer"
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=15
    )

    if response.status_code == 200:
        return response.text

    return ""


def create_report(profile, repositories, summary):

    report = f"""
GITHUB PROFILE ANALYZER
=======================

Generated:
{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

PROFILE
-------

Username: {profile.get("login")}
Name: {profile.get("name") or "Not available"}
Followers: {profile.get("followers", 0)}
Following: {profile.get("following", 0)}
Public Repositories: {profile.get("public_repos", 0)}
Location: {profile.get("location") or "Not available"}

Bio:
{profile.get("bio") or "Not available"}

AI SUMMARY
----------

{summary}

REPOSITORIES
------------

"""

    for repo in repositories:

        report += f"""
Name: {repo.get("name")}
Language: {repo.get("language") or "None"}
Stars: {repo.get("stargazers_count", 0)}
Forks: {repo.get("forks_count", 0)}
URL: {repo.get("html_url")}

"""

    return report


st.markdown("""
<div class="hero">

<h1>🐙 GitHub Profile Analyzer</h1>

<p>Analyze GitHub profiles, repositories and project activity.</p>

</div>
""", unsafe_allow_html=True)


st.markdown("### 🔎 Enter GitHub Profile")

github_input = st.text_input(
    "GitHub URL or Username",
    placeholder="https://github.com/torvalds",
    label_visibility="collapsed"
)


col1, col2, col3 = st.columns([1, 1, 1])

with col2:

    analyze = st.button(
        "🚀 Analyze Profile",
        use_container_width=True,
        type="primary"
    )


if analyze:

    if not github_input:

        st.warning(
            "Please enter a GitHub username or profile URL."
        )

        st.stop()

    username = get_username(github_input)

    try:

        with st.spinner("🔍 Analyzing GitHub profile..."):

            profile = get_profile(username)

            repositories = get_repositories(username)

        st.success("Profile analyzed successfully!")

        st.markdown(
            '<div class="section-title">👤 Profile Overview</div>',
            unsafe_allow_html=True
        )

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.markdown(
                f"""
                <div class="stat-card">
                    <div class="stat-number">
                        {profile.get("followers", 0)}
                    </div>
                    <div class="stat-label">
                        Followers
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col2:

            st.markdown(
                f"""
                <div class="stat-card">
                    <div class="stat-number">
                        {profile.get("following", 0)}
                    </div>
                    <div class="stat-label">
                        Following
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col3:

            st.markdown(
                f"""
                <div class="stat-card">
                    <div class="stat-number">
                        {profile.get("public_repos", 0)}
                    </div>
                    <div class="stat-label">
                        Repositories
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col4:

            total_stars = sum(
                repo.get("stargazers_count", 0)
                for repo in repositories
            )

            st.markdown(
                f"""
                <div class="stat-card">
                    <div class="stat-number">
                        {total_stars}
                    </div>
                    <div class="stat-label">
                        Total Stars
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )


        st.markdown(
            '<div class="section-title">📋 Profile Details</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <div class="profile-card">

            **Username:** `{profile.get("login")}`

            **Name:** {profile.get("name") or "Not available"}

            **Bio:** {profile.get("bio") or "Not available"}

            **Location:** {profile.get("location") or "Not available"}

            </div>
            """,
            unsafe_allow_html=True
        )


        if profile.get("html_url"):

            st.link_button(
                "🌐 Open GitHub Profile",
                profile.get("html_url")
            )


        st.markdown(
            '<div class="section-title">📦 Repositories</div>',
            unsafe_allow_html=True
        )


        repo_data = []

        for repo in repositories:

            repo_data.append({
                "Repository": repo.get("name"),
                "Language": repo.get("language") or "None",
                "⭐ Stars": repo.get("stargazers_count", 0),
                "🍴 Forks": repo.get("forks_count", 0),
                "Updated": repo.get("updated_at", "")[:10]
            })


        st.dataframe(
            repo_data,
            use_container_width=True,
            hide_index=True
        )


        st.markdown(
            '<div class="section-title">📖 README Files</div>',
            unsafe_allow_html=True
        )


        readmes = {}

        progress = st.progress(0)

        total = min(len(repositories), 10)

        for index, repo in enumerate(repositories[:10]):

            repo_name = repo.get("name")

            readme = get_readme(
                username,
                repo_name
            )

            if readme:

                readmes[repo_name] = readme

                with st.expander(
                    f"📄 {repo_name}"
                ):

                    st.markdown(
                        readme[:5000]
                    )

            if total > 0:

                progress.progress(
                    (index + 1) / total
                )

        progress.empty()


        st.markdown(
            '<div class="section-title">🤖 AI Summary</div>',
            unsafe_allow_html=True
        )


        languages = {}

        for repo in repositories:

            language = repo.get("language")

            if language:

                languages[language] = (
                    languages.get(language, 0) + 1
                )


        if languages:

            main_language = max(
                languages,
                key=languages.get
            )

        else:

            main_language = "Not available"


        summary = f"""
### Developer Overview

**{profile.get("name") or profile.get("login")}** has
**{profile.get("public_repos", 0)} public repositories**
and **{profile.get("followers", 0)} followers**.

### Main Programming Language

The most frequently used detected language across the
public repositories is **{main_language}**.

### Repository Activity

The profile contains projects covering:

{", ".join(languages.keys()) if languages else "No language information available."}

### Profile Information

**Bio:** {profile.get("bio") or "Not available"}

**Location:** {profile.get("location") or "Not available"}

This summary is generated from publicly available GitHub
profile and repository information.
"""


        st.info(summary)


        st.markdown(
            '<div class="section-title">📥 Download Report</div>',
            unsafe_allow_html=True
        )


        report = create_report(
            profile,
            repositories,
            summary
        )


        st.download_button(
            "⬇️ Download GitHub Report",
            report,
            file_name=f"{username}_github_report.txt",
            mime="text/plain",
            use_container_width=True
        )


    except requests.exceptions.HTTPError as e:

        if e.response.status_code == 404:

            st.error(
                "❌ GitHub profile not found. "
                "Please check the username."
            )

        elif e.response.status_code == 403:

            st.error(
                "⚠️ GitHub API rate limit reached. "
                "Please try again later."
            )

        else:

            st.error(
                f"GitHub API error: {e}"
            )


    except requests.exceptions.Timeout:

        st.error(
            "⏱️ GitHub request timed out. "
            "Please check your internet connection."
        )


    except requests.exceptions.ConnectionError:

        st.error(
            "🌐 Could not connect to GitHub. "
            "Please check your internet connection."
        )


    except Exception as e:

        st.error(
            f"Something went wrong: {e}"
        )


st.markdown(
    """
    <div class="footer">

    GitHub Profile Analyzer • Built with Python & Streamlit

    </div>
    """,
    unsafe_allow_html=True
)