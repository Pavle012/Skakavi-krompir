#!/bin/bash

# Check if git is installed
if ! command -v git &> /dev/null
then
    echo "git could not be found, please install git."
    exit 1
fi

# Ask for version number
read -p "Enter the version number (e.g., 1.0.0): " version_number

# Validate input (basic validation, ensures it's not empty)
if [ -z "$version_number" ]; then
    echo "Version number cannot be empty. Aborting."
    exit 1
fi

# Create the tag
tag_name="v${version_number}"
echo "Creating git tag: ${tag_name}"
git tag "$tag_name"

# Push the tag
echo "Pushing tag to remote..."
git push origin "$tag_name"

if [ $? -eq 0 ]; then
    echo "Successfully pushed tag ${tag_name}. The release workflow should now be triggered."
else
    echo "Failed to push tag. Please check your git configuration and try again."
fi
