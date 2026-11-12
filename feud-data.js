// Shared data for Prompt Feud.
//   index.html  plays the game
//   admin.html  is the answer key and the session log
// Both read from this file so the board and the answer key cannot drift apart.
//
// Honest provenance: these answers are authored from well-known model defaults,
// not measured from a run of 100 prompts. That is why scoring is rank-based
// (30/25/20/15/10/5) instead of claiming survey counts nobody counted.
(function(){
  var BOARDS = [
    { tag: "Cover letter", level: 1,
      asked: "Ask any chatbot to write a cover letter. Name the opening line it reaches for.",
      answers: [
        { text: "I am writing to express my interest in",
          keys: ["writing to express", "express my interest", "express interest",
                 "writing to apply", "interest in the position"] },
        { text: "I am excited to apply for",
          keys: ["excited to apply", "excited about this opportunity", "excited"] },
        { text: "I am thrilled to apply for",
          keys: ["thrilled to apply", "thrilled", "delighted to apply"] },
        { text: "With a strong background in",
          keys: ["strong background", "extensive background", "background in"] },
        { text: "As a passionate professional",
          keys: ["passionate", "passion for"] },
        { text: "I came across your job posting",
          keys: ["came across your posting", "came across your job", "saw your posting",
                 "came across"] }
      ] },
    { tag: "Resume bullet", level: 3,
      asked: "Ask any chatbot to write a resume bullet. Name the verb it starts with.",
      answers: [
        { text: "Spearheaded", keys: ["spearheaded", "spearhead", "spearheading"] },
        { text: "Leveraged", keys: ["leveraged", "leverage", "leveraging"] },
        { text: "Streamlined", keys: ["streamlined", "streamline", "streamlining"] },
        { text: "Collaborated with cross-functional teams",
          keys: ["collaborated", "collaboration", "cross functional", "crossfunctional"] },
        { text: "Implemented", keys: ["implemented", "implement", "implementing"] },
        { text: "Utilized", keys: ["utilized", "utilize", "utilizing", "utilization"] }
      ] },
    { tag: "Status update", level: 3,
      asked: "Ask any chatbot to write your standup update. Name a phrase it drops in.",
      answers: [
        { text: "Circling back", keys: ["circling back", "circle back"] },
        { text: "Just wanted to touch base", keys: ["touch base", "touching base"] },
        { text: "On track", keys: ["on track", "on schedule", "tracking well"] },
        { text: "Currently blocked on", keys: ["blocked", "blocker", "blockers", "roadblock"] },
        { text: "Moving forward", keys: ["moving forward", "going forward"] },
        { text: "Please let me know if", keys: ["let me know", "please let me know"] }
      ] },
    { tag: "Commit message", level: 2,
      asked: "Ask any chatbot to write a commit message. Name what it writes.",
      answers: [
        { text: "Update README", keys: ["update readme", "readme"] },
        { text: "Fix bug", keys: ["fix bug", "bug fix", "fixed bug", "fix issue", "bugfix"] },
        { text: "Initial commit", keys: ["initial commit", "first commit"] },
        { text: "Refactor code", keys: ["refactor", "refactored", "refactoring"] },
        { text: "Add new feature", keys: ["add feature", "new feature", "added feature"] },
        { text: "Minor changes",
          keys: ["minor changes", "small changes", "various changes", "minor fixes",
                 "misc changes"] }
      ] },
    { tag: "Variable names", level: 4,
      asked: "Ask any chatbot for code holding a list of users. Name the variable it picks.",
      answers: [
        { text: "users", keys: ["users"] },
        { text: "userList", keys: ["userlist", "user list", "users list"] },
        { text: "data", keys: ["data"] },
        { text: "result", keys: ["result", "results"] },
        { text: "items", keys: ["items", "item list", "itemlist"] },
        { text: "userData", keys: ["userdata", "user data"] }
      ] },
    { tag: "Test cases", level: 4,
      asked: "Ask any chatbot to write test cases for a login form. Name a case it lists.",
      answers: [
        { text: "Valid username and password",
          keys: ["valid credentials", "valid username", "valid password", "happy path",
                 "correct credentials", "successful login"] },
        { text: "Invalid password",
          keys: ["invalid password", "wrong password", "incorrect password", "bad password"] },
        { text: "Empty fields",
          keys: ["empty fields", "blank fields", "required fields", "empty", "blank",
                 "left blank", "no input"] },
        { text: "Password reset",
          keys: ["password reset", "forgot password", "reset password"] },
        { text: "SQL injection attempt", keys: ["sql injection", "injection"] },
        { text: "Lockout after failed attempts",
          keys: ["lockout", "locked out", "too many attempts", "failed attempts",
                 "account locked"] }
      ] },
    { tag: "User story", level: 4,
      asked: "Ask any chatbot for a Jira user story. Name the words it uses.",
      answers: [
        { text: "As a user, I want", keys: ["as a user", "i want"] },
        { text: "So that I can", keys: ["so that i can", "so that"] },
        { text: "Acceptance criteria", keys: ["acceptance criteria", "acceptance"] },
        { text: "Given, when, then", keys: ["given when then", "given when", "when then"] },
        { text: "As an admin", keys: ["as an admin", "as an administrator", "admin"] },
        { text: "Definition of done", keys: ["definition of done", "done criteria"] }
      ] },
    { tag: "Slide titles", level: 2,
      asked: "Ask any chatbot to title the slides of a pitch deck. Name a title it gives you.",
      answers: [
        { text: "Key Takeaways", keys: ["key takeaways", "takeaways", "key points"] },
        { text: "The Problem", keys: ["the problem", "problem statement", "problem"] },
        { text: "Our Solution", keys: ["our solution", "the solution", "solution"] },
        { text: "Next Steps", keys: ["next steps", "the road ahead"] },
        { text: "Market Opportunity",
          keys: ["market opportunity", "market size", "the market", "opportunity"] },
        { text: "Thank You", keys: ["thank you", "questions", "q and a", "thanks"] }
      ] },
    { tag: "App ideas", level: 1,
      asked: "Ask any chatbot for a beginner web app idea. Name the app it suggests.",
      answers: [
        { text: "To-do list", keys: ["to do list", "todo list", "todo", "task list",
                                     "to do app", "task tracker"] },
        { text: "Weather app", keys: ["weather app", "weather", "weather dashboard"] },
        { text: "Recipe finder", keys: ["recipe finder", "recipe app", "recipe", "recipes"] },
        { text: "Budget tracker",
          keys: ["budget tracker", "budget app", "budget", "expense tracker", "expenses"] },
        { text: "Personal blog", keys: ["personal blog", "blog", "blogging platform"] },
        { text: "Quiz app", keys: ["quiz app", "quiz", "trivia", "flashcards"] }
      ] },
    { tag: "Hedging", level: 2,
      asked: "Ask any chatbot something it is unsure about. Name how it hedges.",
      answers: [
        { text: "It depends", keys: ["it depends", "depends"] },
        { text: "There are several factors to consider",
          keys: ["several factors", "many factors", "factors to consider",
                 "a few factors", "number of factors"] },
        { text: "I would recommend consulting a professional",
          keys: ["consult a professional", "consulting a professional", "seek professional",
                 "talk to a professional", "ask an expert"] },
        { text: "I do not have access to real-time information",
          keys: ["real time information", "real time data", "no access to",
                 "cannot access", "do not have access"] },
        { text: "As an AI", keys: ["as an ai", "as a language model", "ai language model"] },
        { text: "Generally speaking",
          keys: ["generally speaking", "in general", "typically", "usually"] }
      ] },
    { tag: "Sign-offs", level: 1,
      asked: "Ask any chatbot for anything at all. Name the line it ends on.",
      answers: [
        { text: "Let me know if you have any questions",
          keys: ["let me know", "any questions", "if you have questions"] },
        { text: "I hope this helps", keys: ["hope this helps", "hope that helps"] },
        { text: "Feel free to reach out", keys: ["feel free", "reach out", "dont hesitate"] },
        { text: "Would you like me to",
          keys: ["would you like me to", "want me to", "shall i"] },
        { text: "Happy to help", keys: ["happy to help", "glad to help"] },
        { text: "Good luck", keys: ["good luck", "best of luck"] }
      ] },
    { tag: "Formatting", level: 3,
      asked: "Ask any chatbot a plain question. Name a formatting habit in the answer.",
      answers: [
        { text: "Bullet points", keys: ["bullet points", "bullets", "bulleted list", "bullet"] },
        { text: "Bold headers",
          keys: ["bold headers", "bold text", "headers", "headings", "bold"] },
        { text: "Numbered list", keys: ["numbered list", "ordered list", "numbers"] },
        { text: "Em dashes", keys: ["em dash", "em dashes", "dashes", "dash"] },
        { text: "Here is a breakdown",
          keys: ["a breakdown", "breakdown", "lets break", "break it down"] },
        { text: "A closing summary",
          keys: ["closing summary", "in summary", "summary", "recap", "wrap up"] }
      ] }
  ];

  var FASTMONEY = [
    { q: "Name a word a chatbot uses to start a list.",
      a: ["First", "Additionally", "Moreover", "Furthermore", "To begin"] },
    { q: "Name something a chatbot says it cannot do.",
      a: ["Access real-time information", "Feel emotions", "Browse the web",
          "Remember past conversations", "Make phone calls"] },
    { q: "Name an adjective chatbots overuse.",
      a: ["Robust", "Comprehensive", "Innovative", "Seamless", "Dynamic"] },
    { q: "Name how a chatbot ends an essay.",
      a: ["In conclusion", "To sum up", "Ultimately", "In summary", "All in all"] },
    { q: "Name a punctuation mark chatbots overuse.",
      a: ["Em dash", "Colon", "Semicolon", "Exclamation point", "Parentheses"] },
    { q: "Name the word a chatbot uses instead of \"use\".",
      a: ["Utilize", "Leverage", "Employ", "Harness", "Apply"] },
    { q: "Name the job title a chatbot invents for a fake example.",
      a: ["Software Engineer", "Project Manager", "Marketing Manager",
          "Data Analyst", "Teacher"] },
    { q: "Name the fake company a chatbot puts in an example.",
      a: ["Acme Corp", "TechCorp", "XYZ Company", "Globex", "Innovate Inc"] },
    { q: "Name the placeholder person a chatbot writes about.",
      a: ["John Doe", "Jane Doe", "Alice", "Bob", "Sarah"] },
    { q: "Name how a chatbot opens a reply.",
      a: ["Great question", "Certainly", "Absolutely", "Of course",
          "I would be happy to help"] }
  ];

  // Round 1 draws from level 1, round 4 from level 4 - the night ramps up, and the
  // triple-points round is also the hardest board on the table.
  var ROUND_LEVELS = [1, 2, 3, 4];
  var LEVEL_NAMES = { 1: 'Warm-up', 2: 'Steady', 3: 'Tricky', 4: 'Brutal' };

  window.FEUD = {
    BOARDS: BOARDS,
    ROUND_LEVELS: ROUND_LEVELS,
    LEVEL_NAMES: LEVEL_NAMES,
    FASTMONEY: FASTMONEY,
    POINTS: [30, 25, 20, 15, 10, 5],
    MULTIPLIERS: [1, 1, 2, 3],
    TARGET: 300,
    FAST_TARGET: 200,
    R2_POINTS: 25,
    LOG_KEY: 'promptfeud.log.v1'
  };
})();
