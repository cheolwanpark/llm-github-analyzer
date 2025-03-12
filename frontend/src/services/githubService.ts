// src/services/githubService.ts
import { RepoContext } from "../types";

export const fetchRepoData = async (url: string): Promise<RepoContext> => {
  // Simulate API call delay
  await new Promise((resolve) => setTimeout(resolve, 2000));

  // Extract repo name from URL
  const urlParts = url.split("/");
  const repoName = urlParts[urlParts.length - 1] || "repo";
  const owner = urlParts[urlParts.length - 2] || "owner";

  // Mock data - in a real app this would come from GitHub API
  return {
    url: url,
    name: `${owner}/${repoName}`,
    description: "A modern JavaScript utility library delivering modularity, performance, & extras.",
    stars: 58200,
    forks: 6895,
    issues: 87,
    languages: {
      JavaScript: 89,
      TypeScript: 8,
      HTML: 2,
      CSS: 1,
    },
    contributors: 328,
    lastUpdated: "3 days ago",
    dependencies: ["webpack", "babel", "jest", "eslint", "prettier"],
  };
};

export const generateResponse = async (question: string, repo: RepoContext): Promise<string> => {
  // Simulate AI processing time
  await new Promise((resolve) => setTimeout(resolve, 1000));

  // Generate response based on question and repo context
  if (question.toLowerCase().includes("language") || question.toLowerCase().includes("tech stack")) {
    return `The primary languages used in ${repo.name} are:\n\n${Object.entries(repo.languages)
      .map(([lang, percentage]) => `- **${lang}**: ${percentage}%`)
      .join("\n")}`;
  } else if (question.toLowerCase().includes("depend") || question.toLowerCase().includes("package")) {
    return `The main dependencies for ${repo.name} are:\n\n${repo.dependencies.map((dep) => `- ${dep}`).join("\n")}`;
  } else if (question.toLowerCase().includes("contributor") || question.toLowerCase().includes("maintainer")) {
    return `${repo.name} has **${repo.contributors}** contributors. The repository is actively maintained and was last updated ${repo.lastUpdated}.`;
  } else if (question.toLowerCase().includes("star") || question.toLowerCase().includes("popular")) {
    return `${
      repo.name
    } has **${repo.stars.toLocaleString()}** stars on GitHub, making it a popular repository. It also has ${repo.forks.toLocaleString()} forks.`;
  } else {
    return `Based on my analysis of ${repo.name}, ${repo.description}\n\nThe repository uses primarily ${
      Object.keys(repo.languages)[0]
    } (${repo.languages[Object.keys(repo.languages)[0]]}%) and has an active community with ${
      repo.contributors
    } contributors.\n\nIs there anything specific about the codebase, architecture, or usage patterns you'd like to know?`;
  }
};
