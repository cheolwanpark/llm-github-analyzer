#To test LLM model, send your chunk of text like this:
# post your request to http://localhost:8080/analyze
# data should be repo chunk of text like this:
# would write a bunch of train/test based on this format
import requests
import json
# Define the API endpoint
url = "http://localhost:8080/analyze"

# Define simply structure_payload, This simply payload is from: https://github.com/Robintianqili/markdown-parser/tree/main
Easy_payload = {
    "structure": {
        ".github/workflows": ["main.yml"],
        ".vscode": ["settings.json"],
        "lib": [
            "hamcrest-core-1.3.jar",
            "junit-4.12.jar",
            ".gitignore",
            "MarkdownParse.java",
            "MarkdownParseTest.java",
            "MarkdownParseTestt.java",
            "README.md",
            "Sample.java",
            "Snippet1.md",
            "Snippet2.md",
            "Snippet3.md",
            "TAresults.txt",
            "makefile",
            "mdparse",
            "myresults.txt",
            "test-file.md",
            "test-file2.md",
            "test-file3.md",
            "test-file4.md",
            "test-file5.md",
            "test-file6.md",
            "test-file7.md",
            "test-file8.md",
            "test.md"
        ]
    }
}

# Define the request payload, Thie meduium payload is from: https://github.com/Robintianqili/AI-control-P3D 
Medium_payload = {
    "structure": {
           "AI-control-P3D": [
        "WorkspaceState.json"
    ],
    "FileContainerIndex": [
        "fd43a226-d8b6-4938-82ac-c729e74b9d8f.vsdx",
        "f3476b9e-8721-4f38-98b4-a982d5d748f3.vsdx",
        "25dc96f0-9037-43d8-a6fa-eb243c1565fd.vsdx",
        "9c4dc46e-4dae-41a2-b1b5-a2a2a4a1274d.vsdx"
    ],
    "V17": [],
    "AI_Control": [],
    "AI_Control/RobTianq/AI_Control": [],
    "AI_Control/FileContainerIndex": [
        "b48817f8-ab41-4678-88b0-3d65e7944e45.vsdx"
    ],
    "Properties": [
        "AssemblyInfo.cs",
        "Resource.Designer.cs",
        "Resources.resx",
        "Settings.Designer.cs",
        "Settings.settings"
    ],
    "bin/Debug": [
        "AI_Control.exe",
        "AI_Control.exe.config",
        "AI_Control.pdb",
        "lockheedMartin.Prepar3D.SimConnect.dll",
        "ai_text.xml",
        "ai_text.xsc",
        "config.xml",
        "config.xml.bak"
    ],
    "obj/Debug": [
        "NETFramework,Version=v4.8.AssemblyAttributes.cs",
        "AI_Control.AI_Main.resources",
        "AI_Control.Properties.Resources.resources",
        "AI_Control.csproj.AssemblyReference.cache",
        "AI_Control.csproj.CoreCompileInputs.cache",
        "AI_Control.csproj.FileListAbsolute.txt",
        "AI_Control.csproj.GenerateResource.cache",
        "AI_Control.csproj.AssemblyReference.cache",
        "AI_Control.pdb",
        "DesignTimeResolveAssemblyReferences.cache",
        "DesignTimeResolveAssemblyReferencesInput.cache"
    ],
    "obj/Release": [
        "NETFramework,Version=v4.8.AssemblyAttributes.cs",
        "AI_Control.csproj.AssemblyReference.cache"
    ],
    "src": [
        "AI_Control.cs",
        "AI_Main.cs",
        "AI_Main.Designer.cs",
        "App.config",
        "Devices.cs",
        "Goes.cs",
        "P3D_Interfaces.cs",
        "P3D_Api.cs",
        "P3D_api_utils.cs",
        "Programs.cs"
    ],
    "log": [
        "2024_updates",
        "adjusted_scenario.png",
        "add_load_scenario.png",
        "connected_to_FSX.png",
        "finished_settings.png",
        "new_scenario_2.0X.png",
        "new_scenario_updated.png",
        "P3D_find_and_load_scenario.png",
        "save_scenario_as_last.png",
        "setting_a_scenario.png",
        "start_a_new_simulation.png",
        "202009scenerio_p3dok.png",
        "image_20230927112526.png",
        "trim.png",
        "method_used_for_horizontal_trim.md"
    ],
    "README": [
        "README.md"
    ]
    }
}

Hard_payload = {
    "structure": {
        ".github/workflows": ["gradle.yml"],
        ".gradle/7.4.2": [],
        ".gradle/7.6": [],
        ".gradle/8.0.2": [
            "checksums",
            "dependencies-accessors",
            "executionHistory",
            "fileChanges",
            "fileHashes",
            "gc.properties"
        ],
        "buildOutputCleanup": [
            "buildOutputCleanup.lock",
            "cache.properties",
            "outputFiles.bin"
        ],
        "vcs-1": [
            "gc.properties",
            "file-system.probe"
        ],
        ".vscode": [
            "launch.json",
            "settings.json"
        ],
        "app/bin/main/pantrypal": [
            "AppFrame.class",
            "AudioRecorder$1.class",
            "AudioRecorder.class",
            "CreateView.class",
            "DeleteWindow.class",
            "DetailView.class",
            "Footer.class",
            "GeneratedView.class",
            "Header.class",
            "JavaFXMain.class",
            "Main.class",
            "PerformRequest.class",
            "Recipe.class",
            "RecipeList.class",
            "RecipeView.class"
        ],
        "server": [
            "APIResponse.class",
            "BaseHandler.class",
            "ChatGPTGenerator.class",
            "ChatGPTResponse.class",
            "GenerationHandler.class",
            "MealType.class",
            "MockAPIResponse.class",
            "MockTranscription.class",
            "Recipe.class",
            "RecipeGenerator.class",
            "ServerMain.class",
            "Transcription.class",
            "TranscriptionHandler.class",
            "Whisper.class"
        ],
        "test/server": [
            "RecipeCreationTest.class",
            "RecipeListTest.class",
            "VoiceInputTest.class"
        ],
        "build/classes/java/main/pantrypal": [
            "Account.class",
            "AppFrame.class",
            "AudioRecorder$1.class",
            "AudioRecorder.class",
            "CreateView.class",
            "DeleteWindow.class",
            "DetailView.class",
            "ErrorMessageView.class",
            "Footer.class",
            "GeneratedView.class",
            "Header.class",
            "JavaFXMain.class",
            "LoginView.class",
            "Main.class",
            "MockAccount.class",
            "Observer.class",
            "PerformRequest.class",
            "Recipe.class",
            "RecipeList.class",
            "RecipeView.class",
            "ServerErrorView.class",
            "ServerStatusCheck.class",
            "Subject.class",
            "SuperAccount.class"
        ],
        "test/server": [
            "AccountTest.class",
            "AlphabeticalSortTest.class",
            "ChronologicalSortTest.class",
            "FilterTest.class",
            "ImageTest.class",
            "MealTypeTest.class",
            "MultiplePlatformsTest.class",
            "RecipeCreationTest.class",
            "RecipeListTest.class",
            "RecipeSaveTest.class",
            "RefreshRecipeStoryTest.class",
            "ShareLinkTest.class",
            "US2SortListStoryTest.class",
            "US8ServerErrorStoryTest.class",
            "VoiceInputTest.class"
        ],
        "reports/tests/test/classes": [
            "server.AccountTest.html",
            "server.AlphabeticalSortTest.html",
            "server.ChronologicalSortTest.html",
            "server.FilterTest.html",
            "server.MealTypeTest.html",
            "server.MultiplePlatformsTest.html",
            "server.RecipeCreationTest.html",
            "server.RecipeListTest.html",
            "server.US2SortListStoryTest.html",
            "server.US8ServerErrorStoryTest.html",
            "server.VoiceInputTest.html"
        ],
        "css": [
            "base-style.css",
            "style.css"
        ],
        "js": ["report.js"],
        "packages": ["index.html"],
        "resources/main": [
            "javafx-swt.jar",
            "javafx.base.jar",
            "javafx.controls.jar",
            "javafx.fxml.jar",
            "javafx.graphics.jar",
            "javafx.media.jar",
            "javafx.properties",
            "javafx.swing.jar",
            "javafx.web.jar",
            "json-20230227.jar",
            "junit-platform-console-standalone-1.10.0.jar",
            "opencv-5.8.jar"
        ],
        "test-results/test/binary": [
            "output.bin",
            "output.bin.idx",
            "results.bin",
            "TEST-server.AccountTest.xml",
            "TEST-server.AlphabeticalSortTest.xml",
            "TEST-server.ChronologicalSortTest.xml",
            "TEST-server.FilterTest.xml",
            "TEST-server.MealTypeTest.xml",
            "TEST-server.MultiplePlatformsTest.xml",
            "TEST-server.RecipeCreationTest.xml",
            "TEST-server.RecipeListTest.xml",
            "TEST-server.US2SortListStoryTest.xml",
            "TEST-server.US8ServerErrorStoryTest.xml",
            "TEST-server.VoiceInputTest.xml"
        ],
        "tmp/compileJava/compileTransaction/stash-dir": [
            "ChatGPTGenerator.class.uniqueId0",
            "CreateView.class.uniqueId1",
            "RecipeGenerator.class.uniqueId2",
            "previous-compilation-data.bin"
        ],
        "tmp/compileTestJava/compileTransaction/stash-dir": [
            "previous-compilation-data.bin"
        ],
        "src": [],
        "gradle": [],
        "README.md": [],
        "RecordingServer.mp3": [],
        "StoredRecipe.csv": []
    }
}

# Set headers
headers = {
    "Content-Type": "application/json"
}

# Send the POST request
response = requests.post(url, headers=headers, data=json.dumps(Easy_payload))

# Print the response
print("Easy Response Status Code:", response.status_code)
print("Response JSON:", response.json())
# Store response as plain text
if response.status_code == 200:
    response_data = response.json()
    summary_text = response_data.get("summary", "No summary available.")

    # Save the response as a text file
    with open("Easy_repository_analysis.txt", "w", encoding="utf-8") as file:
        file.write(summary_text)

    print(" Response saved successfully to `repository_analysis.txt`")
else:
    print(f"Error {response.status_code}: {response.text}")




# Send the POST request
response = requests.post(url, headers=headers, data=json.dumps(Medium_payload))
# Store response as plain text
if response.status_code == 200:
    response_data = response.json()
    summary_text = response_data.get("summary", "No summary available.")

    # Save the response as a text file
    with open("Medium_repository_analysis.txt", "w", encoding="utf-8") as file:
        file.write(summary_text)

    print(" Response saved successfully to `repository_analysis.txt`")
else:
    print(f" Error {response.status_code}: {response.text}")
# Print the response
print("Medium payload Code:", response.status_code)
print("Response JSON:", response.json())





# Send the POST request
response = requests.post(url, headers=headers, data=json.dumps(Hard_payload))

# Print the response
print("Hard payload Response Status Code:", response.status_code)
print("Response JSON:", response.json())
# Store response as plain text
if response.status_code == 200:
    response_data = response.json()
    summary_text = response_data.get("summary", "No summary available.")

    # Save the response as a text file
    with open("Hard_repository_analysis.txt", "w", encoding="utf-8") as file:
        file.write(summary_text)

    print(" Response saved successfully to `repository_analysis.txt`")
else:
    print(f" Error {response.status_code}: {response.text}")