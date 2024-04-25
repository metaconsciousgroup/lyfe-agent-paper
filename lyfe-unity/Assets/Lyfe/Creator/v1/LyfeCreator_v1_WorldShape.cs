using UnityEngine;

namespace Lyfe.Creator.v1
{
    public class LyfeCreator_v1_WorldShape : MonoBehaviour
    {
        public LyfeCreator_v1_WorldShapeKind kind;
        public float radiusMin;
        public float radiusMax;
        public Vector3 sizeMin;
        public Vector3 sizeMax;
        

#if UNITY_EDITOR
        public static void DrawGizmo(LyfeCreator_v1_WorldShape source)
        {
            Transform transform = source.transform;
            LyfeCreator_v1_WorldShapeKind kind = source.kind;
            float radiusMin = source.radiusMin;
            float radiusMax = source.radiusMax;
            Vector3 sizeMin = source.sizeMin;
            Vector3 sizeMax = source.sizeMax;
            UnityEditor.Handles.color = Color.magenta;

            switch (kind)
            {
                case LyfeCreator_v1_WorldShapeKind.Circle:
                {
                    DrawCircle(transform, radiusMin, Color.green);
                    DrawCircle(transform, radiusMax, Color.red);
                    break;
                }
                case LyfeCreator_v1_WorldShapeKind.Rect:
                {
                    DrawCube(transform, sizeMin, Color.green);
                    DrawCube(transform, sizeMax, Color.red);
                    break;
                }
                case LyfeCreator_v1_WorldShapeKind.Sphere:
                {
                    DrawSphere(transform, radiusMin, Color.green);
                    DrawSphere(transform, radiusMax, Color.red);
                    break;
                }
            }

        }

        private static void DrawCircle(Transform pivot, float radius, Color color)
        {
            if (radius == 0f) return;

            UnityEditor.Handles.matrix = Matrix4x4.TRS(pivot.position, pivot.rotation, Vector3.one);
            UnityEditor.Handles.color = color;
            UnityEditor.Handles.DrawWireDisc(Vector3.zero, Vector3.up, radius);
        }

        private static void DrawCube(Transform pivot, Vector3 size, Color color)
        {
            UnityEditor.Handles.matrix = Matrix4x4.TRS(pivot.position, pivot.rotation, Vector3.one);
            UnityEditor.Handles.color = color;
            UnityEditor.Handles.DrawWireCube(Vector3.zero, size);
        }

        private static void DrawSphere(Transform pivot, float radius, Color color)
        {
            UnityEditor.Handles.matrix = Matrix4x4.TRS(pivot.position, pivot.rotation, Vector3.one);
            UnityEditor.Handles.color = color;
            UnityEditor.Handles.RadiusHandle(Quaternion.identity, Vector3.zero, radius, false);
        }
#endif
    }
}
