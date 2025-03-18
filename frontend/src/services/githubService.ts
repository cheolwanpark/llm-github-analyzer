// src/services/githubService.ts
import { WELCOME_PROMPT } from "../prompts";
import { RepoContext } from "../types";

export const initializeAnalyzer = async (githubUrl: string): Promise<string> => {
  try {
    const response = await fetch("http://localhost:8000/analyzer", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ github_url: githubUrl }),
    });

    if (!response.ok) {
      throw new Error(`Failed to initialize analyzer: ${response.status}`);
    }

    const data = await response.json();
    return data.analyzer_id;
  } catch (error) {
    console.error("Error initializing analyzer:", error);
    throw error;
  }
};

export const waitForAnalyzerReady = async (analyzerId: string, interval = 3000, maxAttempts = 15): Promise<boolean> => {
  let attempts = 0;

  while (attempts < maxAttempts) {
    try {
      const response = await fetch(`http://localhost:8000/analyzer/${analyzerId}`);
      const data = await response.json();

      console.log(`Analyzer status: ${data.progress} (attempt ${attempts + 1}/${maxAttempts})`);
      if (data.progress === "READY") {
        return true; // Analyzer is ready
      }
    } catch (error) {
      console.error("Error checking analyzer status:", error);
    }

    attempts++;
    await new Promise((resolve) => setTimeout(resolve, interval)); // Wait before retrying
  }

  console.error("Analyzer did not become READY in time.");
  return false; // Timed out
};

export const submitQuery = async (analyzerId: string, queryText: string): Promise<string> => {
  try {
    const response = await fetch("http://localhost:8000/query", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        analyzer_id: analyzerId,
        query: queryText,
      }),
    });

    if (!response.ok) {
      throw new Error(`Failed to submit query: ${response.status}`);
    }

    const data = await response.json();
    return data.query_id;
  } catch (error) {
    console.error("Error submitting query:", error);
    throw error;
  }
};

export const waitForQueryDone = async (queryId: string, interval = 4500, maxAttempts = 25) => {
  let attempts = 0;

  while (attempts < maxAttempts) {
    try {
      const response = await fetch(`http://localhost:8000/query/${queryId}`);
      const data = await response.json();

      console.log(`Query status: ${data.progress} (attempt ${attempts + 1}/${maxAttempts})`);
      if (data.progress === "DONE") {
        return data.result; // Query is done, return the result
      }
    } catch (error) {
      console.error("Error checking query status:", error);
    }

    attempts++;
    await new Promise((resolve) => setTimeout(resolve, interval)); // Wait before retrying
  }

  console.error("Query did not complete in time.");
  return null; // Timed out
};

// submits query, waits for it to be done, returns only the answer
export async function fetchQueryAnswer(analyzerID: string, prompt: string) {
  try {
    // Step 1: Submit Query
    const queryID = await submitQuery(analyzerID, prompt);
    console.log("Query ID:", queryID);

    // Step 2: Wait for Query Completion
    const { result } = await waitForQueryDone(queryID);

    // Step 3: Process Result
    return result ? result.answer : "Query did not complete in time.";
  } catch (error) {
    console.error("Error processing query:", error);
    return "An error occurred while fetching the query result.";
  }
}

// export const fetchRepoData = async (url: string): Promise<RepoContext> => {
//   // Simulate API call delay
//   await new Promise((resolve) => setTimeout(resolve, 2000));

//   // Extract repo name from URL
//   const urlParts = url.split("/");
//   const repoName = urlParts[urlParts.length - 1] || "repo";
//   const owner = urlParts[urlParts.length - 2] || "owner";

//   // Mock data - in a real app this would come from GitHub API
//   return {
//     url: url,
//     name: `${owner}/${repoName}`,
//     description: "A modern JavaScript utility library delivering modularity, performance, & extras.",
//     stars: 58200,
//     forks: 6895,
//     issues: 87,
//     languages: {
//       JavaScript: 89,
//       TypeScript: 8,
//       HTML: 2,
//       CSS: 1,
//     },
//     contributors: 328,
//     lastUpdated: "3 days ago",
//     dependencies: ["webpack", "babel", "jest", "eslint", "prettier"],
//   };
// };

// export const generateResponse = async (question: string, repo: RepoContext): Promise<string> => {
//   console.log("bruhdfsdas");
//   // Simulate AI processing time
//   await new Promise((resolve) => setTimeout(resolve, 1000));

//   // Generate response based on question and repo context
//   if (question.toLowerCase().includes("language") || question.toLowerCase().includes("tech stack")) {
//     return `The primary languages used in ${repo.name} are:\n\n${Object.entries(repo.languages)
//       .map(([lang, percentage]) => `- **${lang}**: ${percentage}%`)
//       .join("\n")}`;
//   } else if (question.toLowerCase().includes("depend") || question.toLowerCase().includes("package")) {
//     return `The main dependencies for ${repo.name} are:\n\n${repo.dependencies.map((dep) => `- ${dep}`).join("\n")}`;
//   } else if (question.toLowerCase().includes("contributor") || question.toLowerCase().includes("maintainer")) {
//     return `${repo.name} has **${repo.contributors}** contributors. The repository is actively maintained and was last updated ${repo.lastUpdated}.`;
//   } else if (question.toLowerCase().includes("star") || question.toLowerCase().includes("popular")) {
//     return `${
//       repo.name
//     } has **${repo.stars.toLocaleString()}** stars on GitHub, making it a popular repository. It also has ${repo.forks.toLocaleString()} forks.`;
//   } else {
//     return `Based on my analysis of ${repo.name}, ${repo.description}\n\nThe repository uses primarily ${
//       Object.keys(repo.languages)[0]
//     } (${repo.languages[Object.keys(repo.languages)[0]]}%) and has an active community with ${
//       repo.contributors
//     } contributors.\n\nIs there anything specific about the codebase, architecture, or usage patterns you'd like to know?`;
//   }
// };
