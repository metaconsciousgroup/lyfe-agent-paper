#!/bin/bash
set -e

# Check if there are any untracked or modified files that are not bash scripts
if git ls-files --others --exclude-standard -- '*.sh' | grep -q .; then
    echo "There are untracked files that are not bash scripts."
    echo "Please commit or stash them before continuing."
    exit 1
fi

source .env

GIT_HASH=$(git rev-parse HEAD)
echo "Git hash: $GIT_HASH"

echo "Building Unity project..."
PROJECT_PATH=$(pwd)/..
$UNITY_EDITOR_BINARY_PATH -batchmode -nographics -quit -projectPath $PROJECT_PATH -executeMethod ExtendedBuildScript.BuildAllTargets

current_dir="$PWD"
echo "Packaging Dedicated Server..."
( 
    cd $PROJECT_PATH/Builds/Linux && \
    zip -r $current_dir/linux-server.zip . -x "*.DS_Store" 
)
echo "Packaging Dedicated Server... Done!"

echo "Packaging WebGL Client..."
(
    cd $PROJECT_PATH/Builds/WebGL/LyfeGameClient && \
    zip -r $current_dir/webgl-client.zip . -x "*.DS_Store"
)
echo "Packaging WebGL Client... Done!"

echo "Packaging Mac Standalone Client..."
(
    cd $PROJECT_PATH/Builds/macOS && \
    codesign -s "$MAC_CERTIFICATE_NAME" -f LyfeGameClient.app && \
    zip -r $current_dir/mac-client.zip LyfeGameClient.app -x "*.DS_Store"
)
echo "Packaging Mac Standalone Client... Done!"

echo "Packaging Mac Development Build..."
(
    cd $PROJECT_PATH/Builds/macOS && \
    codesign -s "$MAC_CERTIFICATE_NAME" -f LyfeGame_Development.app && \
    zip -r $current_dir/mac-dev-build.zip LyfeGame_Development.app -x "*.DS_Store"
)
echo "Packaging Mac Development Build... Done!"

echo "Packaging Mac Server..."
(
    cd $PROJECT_PATH/Builds/macOS && \
    codesign -s "$MAC_CERTIFICATE_NAME" -f LyfeGame_Host.app && \
    zip -r $current_dir/mac-server.zip LyfeGame_Host.app -x "*.DS_Store"
)

echo "Packaging Windows Standalone Client..."
(
    cd $PROJECT_PATH/Builds/Windows && \
    zip -r $current_dir/windows-client.zip . -x "*.DS_Store"
)

echo "Uploading builds to S3..."
aws s3 cp linux-server.zip s3://$S3_GAME_BUILD_BUCKET/$GIT_HASH/linux-server.zip --metadata tag=$GIT_HASH
aws s3 cp webgl-client.zip s3://$S3_GAME_BUILD_BUCKET/$GIT_HASH/webgl-client.zip --metadata tag=$GIT_HASH
aws s3 cp mac-client.zip s3://$S3_GAME_BUILD_BUCKET/$GIT_HASH/mac-client.zip --metadata tag=$GIT_HASH
aws s3 cp mac-dev-build.zip s3://$S3_GAME_BUILD_BUCKET/$GIT_HASH/mac-dev-build.zip --metadata tag=$GIT_HASH
aws s3 cp mac-server.zip s3://$S3_GAME_BUILD_BUCKET/$GIT_HASH/mac-server.zip --metadata tag=$GIT_HASH
aws s3 cp windows-client.zip s3://$S3_GAME_BUILD_BUCKET/$GIT_HASH/windows-client.zip --metadata tag=$GIT_HASH

aws s3 sync $PROJECT_PATH/Builds/WebGL/LyfeGameClient s3://$S3_GAME_BUILD_BUCKET/$GIT_HASH/WebGL/ --delete --exclude "*.br"  --exclude ".DS_Store" --metadata tag=$GIT_HASH
aws s3 sync $PROJECT_PATH/Builds/WebGL/LyfeGameClient s3://$S3_GAME_BUILD_BUCKET/$GIT_HASH/WebGL/ --delete --include "*.br" --content-encoding "br" --metadata tag=$GIT_HASH

echo "Uploading builds to S3... Done!"
