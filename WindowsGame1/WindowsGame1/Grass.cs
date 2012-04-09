using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using Microsoft.Xna.Framework;

namespace WindowsGame1
{
    class Grass
    {
        private readonly Elastic _angles;
        private readonly Vector2 _position;
        private readonly Vector2 _length;

        private readonly Color _color;

        public Vector2 Position { get { return _position; } }

        public Grass(Vector2 position, Vector2 length, Vector2 k, Color color, float friction)
        {
            _position = position;
            _length = length;
            _angles = new Elastic()
                          {
                              Origin = new Vector2((float)(-Math.PI / 2), (float)(0)),
                              Friction = friction,
                              Position = new Vector2((float)(-Math.PI / 2), (float)(0)),
                              Speed = new Vector2(),
                              K = k
                          };
            _color = color;
        }

        public void Draw(SpriteBatchEx spriteBatch, GameTime time)
        {
            _angles.Update(time);

            spriteBatch.DrawLine(_position, _angles.Position.X, _length.X, _color, 4);

            Vector2 pos2 = new Vector2
                               {
                                   X = _position.X + (float) Math.Cos(_angles.Position.X)*_length.X,
                                   Y = _position.Y + (float) Math.Sin(_angles.Position.X)*_length.X
                               };

            //Vector2 pos3;
            //pos3.X = pos2.X + (float)Math.Cos(_angles.Position.X + _angles.Position.Y) * _length.Y;
            //pos3.Y = pos2.Y - (float)Math.Sin(_angles.Position.X + _angles.Position.Y) * _length.Y;

            spriteBatch.DrawLine(pos2, _angles.Position.X + _angles.Position.Y, _length.Y, _color, 2);

        }

        internal void AddSpeed(Vector2 speed)
        {
            _angles.Speed += speed;
        }
    }
}
