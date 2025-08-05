import yaml

# Create a simple test set for demonstration
test_set = {
    "Voyager Program": [
        "What was the primary mission of the Voyager spacecraft?",
        "When were the Voyager spacecraft launched?",
        "What is the Golden Record and what does it contain?",
        "How far have the Voyager spacecraft traveled?",
        "What instruments do the Voyager spacecraft carry?"
    ],
    "Chernobyl Disaster": [
        "What caused the Chernobyl nuclear disaster?",
        "When did the Chernobyl disaster occur?",
        "What were the immediate effects of the Chernobyl disaster?",
        "How did the Chernobyl disaster affect the environment?",
        "What safety measures were implemented after Chernobyl?"
    ],
    "Periodic Table": [
        "Who created the first periodic table?",
        "How are elements organized in the periodic table?",
        "What are the main groups in the periodic table?",
        "What is the atomic number and what does it represent?",
        "How do elements in the same group behave similarly?"
    ]
}

# Save the test set to YAML file
with open("testset.yaml", "w") as f:
    yaml.dump(test_set, f, default_flow_style=False, indent=2)

print("Test set generated and saved to testset.yaml")
print(f"Generated {len(test_set)} subjects with {sum(len(questions) for questions in test_set.values())} total questions") 