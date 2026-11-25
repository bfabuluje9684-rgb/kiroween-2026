# Requirements Document

## Introduction

FrankySense is a Halloween-themed browser-based quiz game targeting beginner students learning Python basics. Players answer multiple-choice questions on topics including variables, data types, conditions, loops, functions, and lists. Every wrong answer causes Franky — a Frankenstein-style monster — to grow by one stage. The monster has five stages; reaching Stage 5 ends the game. Stages 1 through 4 are safe. The player wins by completing the question set with three or fewer wrong answers. An AI model API generates questions and explanatory feedback, but all answer-checking logic runs in backend code — never delegated to the AI.

---

## Glossary

- **Game**: The FrankySense web application as a whole.
- **Player**: A beginner student who interacts with the Game through a browser.
- **Question**: A multiple-choice Python-basics quiz item with exactly one correct answer and three distractors; sourced from the AI_Service or the Question_Bank.
- **Answer**: One of the four choices the Player selects for a Question.
- **Correct_Answer**: The single answer option that the Backend marks as correct for a given Question.
- **Wrong_Answer**: Any Answer that is not the Correct_Answer.
- **Franky**: The in-game monster whose growth tracks Player mistakes.
- **Stage**: One of five discrete size levels of Franky (1 = tiny, 2 = small, 3 = medium, 4 = large, 5 = devours).
- **Game_Over**: The state reached when Franky reaches Stage 5; the session ends.
- **Win**: The state reached when the Player answers all Questions before Franky reaches Stage 5.
- **Weak_Spot**: A Topic the Player answered wrongly at least once in the current Session; recorded in the order the wrong answers occurred.
- **Session**: A single play-through from game start to Win or Game_Over.
- **Backend**: The Python server that generates Questions, validates Answers, and manages Session state.
- **Frontend**: The React/JavaScript browser UI that displays Questions and Franky's current Stage.
- **AI_Service**: The external AI model API called by the Backend to generate Questions and feedback text.
- **Feedback**: A short plain-language explanation returned after each Answer, explaining why the Correct_Answer is right.
- **Topic**: One of the six Python-basics subjects (variables, data types, conditions, loops, functions, lists).
- **Env_File**: A `.env` file on the server that holds the AI_Service API key; never committed to version control.
- **Question_Bank**: The built-in set of at least 20 hand-written Questions stored in the Backend, used as a fallback when the AI_Service is unavailable or a generated Question fails validation.

---

## Requirements

### Requirement 1: Start a New Game Session

**User Story:** As a Player, I want to start a new game, so that I can begin answering Python questions with Franky at Stage 1.

#### Acceptance Criteria

1. WHEN the Player clicks the Start button, THE Backend SHALL create a new Session with Franky at Stage 1 and zero wrong answers recorded.
2. WHEN a new Session is created, THE Frontend SHALL display Franky's Stage 1 visual and the first Question.
3. THE Backend SHALL generate the Session's ten Questions in parallel with a total time limit of 15 seconds for the whole batch; any Question not ready within 15 seconds SHALL be replaced with a Question from the Question_Bank, so that the Session starts without per-answer latency.
4. WHEN the Backend generates Questions, THE AI_Service SHALL be called with a prompt that specifies the Topic, difficulty level appropriate for beginners, and a request for exactly one correct answer and three distractor answers.

---

### Requirement 2: Display Questions and Answer Choices

**User Story:** As a Player, I want to see a clear question and four answer options, so that I can make an informed choice.

#### Acceptance Criteria

1. WHEN a Question is presented, THE Frontend SHALL display the question text and exactly four labeled answer options.
2. THE Frontend SHALL apply a dark, spooky visual style with text contrast sufficient for readability (WCAG AA minimum).
3. WHEN the Player has not yet submitted an Answer for the current Question, THE Frontend SHALL keep all four answer options selectable.
4. THE Backend SHALL ensure every Question covers exactly one Topic drawn from: variables, data types, conditions, loops, functions, or lists.

---

### Requirement 3: Validate Answers in Backend Code

**User Story:** As a Player, I want the game to tell me whether my answer is right or wrong, so that I can learn from mistakes.

#### Acceptance Criteria

1. WHEN the Player selects an Answer and submits it, THE Backend SHALL compare the selected Answer to the stored Correct_Answer and return a result of "correct" or "wrong".
2. THE Backend SHALL determine the correct/wrong result using stored answer data — never by sending the Player's Answer to the AI_Service for grading.
3. WHEN the Backend returns a result, THE Frontend SHALL display the result clearly before showing the next Question.
4. WHEN the Backend returns a result, THE Backend SHALL include the Feedback text that was stored with the Question when it was created; no additional AI_Service call is made at answer time.
5. IF the stored Feedback for a Question is empty or missing, THEN THE Backend SHALL return a default fallback Feedback message in its place.
6. THE Frontend SHALL proceed to the next Question regardless of whether Feedback text is present in the Backend response; Feedback display is non-blocking.

---

### Requirement 4: Monster Growth on Wrong Answers

**User Story:** As a Player, I want to see Franky grow each time I answer wrong, so that I feel the stakes of my mistakes.

#### Acceptance Criteria

1. WHEN the Backend records a Wrong_Answer, THE Backend SHALL increment Franky's Stage by exactly one.
2. WHEN Franky's Stage increases, THE Frontend SHALL display the visual corresponding to the new Stage without requiring a full page reload.
3. WHILE Franky's Stage is 1, 2, 3, or 4, THE Frontend SHALL allow the Player to continue to the next Question.
4. THE Backend SHALL not change Franky's Stage when the Player submits a Correct_Answer.
5. WHEN the Player submits a Correct_Answer, THE Frontend SHALL show a positive confirmation without changing Franky's Stage visual.
6. WHEN a Wrong_Answer moves Franky to Stage 5, THE Frontend SHALL display the wrong-answer result, the Feedback text, and the Stage 5 Franky visual, then SHALL present a Continue button; WHEN the Player clicks Continue, THE Frontend SHALL transition to the Game_Over screen.

---

### Requirement 5: Game Over When Monster Reaches Stage 5

**User Story:** As a Player, I want the game to end dramatically when I make too many mistakes, so that the stakes feel real.

#### Acceptance Criteria

1. WHEN the Backend records a Wrong_Answer that moves Franky to Stage 5, THE Backend SHALL set the Session state to Game_Over.
2. WHEN the Backend sets the Session state to Game_Over and the Player clicks Continue on the Stage 5 result screen, THE Frontend SHALL transition to the Game_Over screen.
3. WHEN the Game_Over screen is displayed, THE Frontend SHALL show the Player's final score (number of Correct_Answers) and total questions attempted.
4. WHEN the Player selects Play Again from the Game_Over screen, THE Frontend SHALL start a new Session and THE Backend SHALL discard the previous Session, so that only the new active Session exists going forward.

---

### Requirement 6: Win Condition

**User Story:** As a Player, I want to win the game by completing all questions without letting Franky reach Stage 5, so that I feel rewarded for learning.

#### Acceptance Criteria

1. WHEN the Player answers the final Question and Franky's Stage is 1, 2, 3, or 4, THE Backend SHALL set the Session state to Win.
2. WHEN the Session state is Win, THE Frontend SHALL display a victory screen with a congratulatory message.
3. WHEN the victory screen is displayed, THE Frontend SHALL show the Player's final score and the number of wrong answers made.
4. WHEN the Player selects Play Again from the victory screen, THE Frontend SHALL start a new Session and THE Backend SHALL discard the previous Session, so that only the new active Session exists going forward.

---

### Requirement 7: Question Topics and Coverage

**User Story:** As a Player, I want questions drawn from all six Python-basics topics, so that I learn a broad set of fundamentals.

#### Acceptance Criteria

1. THE Backend SHALL generate Questions covering all six Topics (variables, data types, conditions, loops, functions, lists) within a single Session.
2. WHEN a Session contains ten or more Questions, THE Backend SHALL include at least one Question per Topic.
3. THE AI_Service prompt SHALL specify the target Topic for each Question so that generated content is on-topic.

---

### Requirement 8: AI-Generated Questions and Feedback

**User Story:** As a Player, I want varied, freshly generated questions each session, so that the game stays challenging across multiple play-throughs.

#### Acceptance Criteria

1. WHEN the Backend requests a Question from the AI_Service, THE Backend SHALL send a structured prompt specifying: Topic, beginner difficulty, four answer choices, and designation of the Correct_Answer.
2. WHEN the AI_Service responds, THE Backend SHALL parse the response and store: question text, four answer options, the index of the Correct_Answer, and the Feedback text.
3. THE Backend SHALL validate that the parsed Question contains exactly four answer options and exactly one designated Correct_Answer before storing it; IF the validation fails, THE Backend SHALL make one replacement request to the AI_Service; IF the replacement Question also fails validation, THE Backend SHALL substitute a Question from the built-in bank; at most two AI_Service calls are made per Question slot.
4. FOR ALL Questions stored in a Session, parsing the AI_Service response and re-serializing the Question data SHALL produce equivalent question text, options, correct answer index, and feedback (round-trip property).
5. WHEN the Backend calls the AI_Service, THE Backend SHALL apply a timeout of 10 seconds; IF the AI_Service does not respond within 10 seconds, THE Backend SHALL treat the call as unavailable and substitute a Question from the built-in bank.

---

### Requirement 9: Secure API Key Handling

**User Story:** As a developer, I want API keys kept out of the repository, so that credentials are never exposed publicly.

#### Acceptance Criteria

1. THE Backend SHALL read the AI_Service API key exclusively from the Env_File at server startup.
2. THE Backend SHALL not log, return in any API response, or embed in any source file the AI_Service API key.
3. IF the Env_File is absent or the AI_Service API key is missing on startup, THEN THE Backend SHALL log a warning and continue to start using only the built-in question bank.
4. THE Game repository SHALL include a `.gitignore` entry that excludes the Env_File from version control.

---

### Requirement 10: Session State Integrity

**User Story:** As a Player, I want the game to track my progress accurately throughout a session, so that scores and monster stage are always correct.

#### Acceptance Criteria

1. THE Backend SHALL store Session state server-side, including: current Question index, Franky's Stage, count of Correct_Answers, and count of Wrong_Answers.
2. WHEN the Player submits an Answer, THE Backend SHALL update Session state atomically before returning the result to the Frontend.
3. WHILE a Session is active, THE Backend SHALL reject any request to submit an Answer for a Question index that has already been answered, and SHALL return an error response.
4. IF the Backend receives an Answer submission when the Session state is Game_Over or Win, THEN THE Backend SHALL return an error response indicating the Session has ended.

---

### Requirement 11: Code Quality and Maintainability

**User Story:** As a first-year student developer, I want the codebase to be simple and well-commented, so that I can understand every line.

#### Acceptance Criteria

1. THE Backend SHALL organise source files so that each file has a single responsibility (e.g., routing, AI integration, session management, answer validation are in separate files).
2. THE Frontend SHALL organise React components so that each component file has a single responsibility (e.g., question display, monster display, score display are separate components).
3. THE Backend source files SHALL include inline comments on non-obvious logic that explain why the code does what it does, not only what it does.
4. THE Frontend source files SHALL include inline comments on non-obvious logic that explain why the code does what it does, not only what it does.

---

### Requirement 12: Built-In Question Bank

**User Story:** As a Player, I want the game to keep working even when the AI service is unavailable, so that I can always practise.

#### Acceptance Criteria

1. THE Backend SHALL include a built-in bank of at least 20 hand-written Questions with correct answers and Feedback, covering all six Topics with at least three Questions per Topic.
2. WHEN the AI_Service is unavailable or the API key is missing, THE Backend SHALL draw Questions from the built-in bank instead of calling the AI_Service.
3. WHEN an AI_Service Question fails validation twice, THE Backend SHALL substitute a Question from the built-in bank for that slot.
4. THE built-in bank Questions SHALL conform to the same schema as AI-generated Questions (question text, four answer options, correct answer index, Feedback text).

---

### Requirement 13: No Duplicate Questions in a Session

**User Story:** As a Player, I want every question in a session to be unique, so that I am not asked the same question twice.

#### Acceptance Criteria

1. THE Backend SHALL ensure that no Question appears more than once within the same Session.
2. WHEN selecting Questions from the Question_Bank to fill a Session, THE Backend SHALL track which Questions have already been selected and SHALL NOT select the same Question again for that Session.
3. WHEN the Backend generates Questions in parallel, THE Backend SHALL assign each AI_Service call a different Topic or subtopic so that the prompts themselves are distinct.
4. AFTER all parallel AI_Service calls complete, THE Backend SHALL compare the question text of every generated Question and, IF any two Questions have identical text, THE Backend SHALL replace the duplicate with an unused Question from the Question_Bank.
5. IF the duplicate-detection step fails or is unavailable, THE Backend SHALL proceed with the Questions it has without blocking Session start.

---

### Requirement 14: Limit AI Usage

**User Story:** As the developer, I want AI-powered question generation limited per visitor, so that strangers cannot use up my AI credits.

#### Acceptance Criteria

1. THE Backend SHALL allow each visitor (identified by IP address) at most 5 AI-powered Sessions per hour.
2. WHEN a visitor exceeds that limit, THE Backend SHALL still start the Session using only the Question_Bank, so the game stays playable.
3. THE Backend SHALL allow at most 200 AI-powered Sessions per day across all visitors, after which all new Sessions use only the Question_Bank until the next day.
4. THE Backend SHALL keep these limits in simple in-memory counters, with no database.

---

### Requirement 15: Franky Is Stitched From Weak Spots

**User Story:** As a Player, I want Franky to be built from the topics I got wrong, so that I can see exactly which parts of Python I need to practise.

#### Acceptance Criteria

1. THE Backend SHALL record the Topic of every Wrong_Answer in the Session as a Weak_Spot, in the order the wrong answers happened.
2. WHEN a Wrong_Answer is recorded, THE Frontend SHALL show Franky growing by attaching a stitched body part that belongs to that Topic; each of the six Topics has its own distinct body part.
3. IF the Player gets a second Wrong_Answer in a Topic that already has a body part attached, THEN THE Frontend SHALL show that part with an extra stitch or glow instead of adding a new part.
4. THE Backend SHALL include the list of Weak_Spots in every answer response.
5. WHEN the Game_Over screen or the victory screen is displayed, THE Frontend SHALL show a summary naming each Weak_Spot Topic and how many times it was missed, for example "Franky is stitched from your weak spots: loops (2), functions (1)".
6. IF the Player finishes with no Wrong_Answers, THEN the victory screen SHALL say that Franky stayed tiny because there were no weak spots.
